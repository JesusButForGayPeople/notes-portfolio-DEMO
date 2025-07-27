---
layout: post
title: Coordinate Systems in Mirador
---

Mirador uses multiple coordinate systems to bridge the gap between 2D maze representation and 3D navigation. Understanding how these systems interact is crucial for implementing game mechanics and ensuring consistent behavior across different parts of the engine.

## Maze Grid Coordinate System

The grid system provides a 2D wrapper for maze representation:
- Grid positions use `row` and `col` parameters
- Origin `(0, 0)` is at the top-left corner
- The maze structure is a 2D boolean array where `true` values represent walls and `false` values represent pathways

The implementation uses a `Cell` struct to encapsulate maze positions:

```rust
struct Cell {
    row: usize,
    col: usize,
}
```

In Mirador's implementation, the maze entry point is at the bottom-left cell, expressed as `(height-1, 0)` in grid coordinates. This position serves as the player's starting location. The exit cell is placed during maze generation and marked with an asterisk character (`*`) in serialized maze files.

## World Coordinate System (3D)

To create an immersive navigation experience, Mirador translates the 2D maze into a 3D world coordinate system that handles both rendering and collision physics. This is the space where players spend most of their time.

The 3D system uses a position vector `[x, y, z]` where:
- `x`: horizontal position (positive = east/right)
- `y`: vertical elevation (positive = up)
- `z`: depth (positive = south/backward)

Key characteristics include:
- Origin placement at `[0.0, 0.0, 0.0]` (center of the floor)
- Standard right-handed coordinate system
- Integration with rendering pipelines through `math/vec.rs`

## Grid-to-World Mapping

The transformation between coordinate systems uses adaptive scaling to ensure mazes of varying dimensions fit proportionally within the constrained floor space:

- The game floor spans `FLOOR_SIZE = 3000.0` world units square
- The maze is centered at the world origin to maximize available space
- Individual cell size is calculated dynamically based on maze dimensions:

```rust
let cell_size = floor_size / max(maze_width, maze_height) as f32;
```

The system determines precise world coordinates by calculating offsets from the origin:

```rust
let origin_x = -(maze_width as f32 * cell_size) / 2.0;
let origin_z = -(maze_height as f32 * cell_size) / 2.0;
```

This approach maintains consistent cell size while ensuring the maze fits within the available world space.

## Player Positioning

Mirador's player positioning system uses coordinate transformation to place the player at the maze entrance. When a new level initializes, the following function positions the player appropriately:

```rust
pub fn spawn_at_maze_entrance(&mut self, maze_grid: &[Vec<bool>]) {
    let maze_dimensions = (maze_grid[0].len(), maze_grid.len());
    let entrance_cell = coordinates::get_bottom_left_cell(maze_dimensions);
    self.position = coordinates::maze_to_world(&entrance_cell, maze_dimensions, PLAYER_HEIGHT);
    self.current_cell = entrance_cell;
    self.yaw = coordinates::direction_to_yaw(coordinates::Direction::North);
}
```

This initialization sets the player's elevation to `PLAYER_HEIGHT` (50.0 world units), facing northward (yaw = 0°) with a slight downward view angle (pitch = 3°). This orientation provides an optimal perspective for maze navigation.

## Direction and Orientation

### Player Movement

Mirador implements player movement through trigonometric calculations that translate user input into movement delta vectors. This approach creates intuitive navigation that responds correctly to the player's current orientation:

```rust
let forward_x = self.yaw.to_radians().sin();
let forward_z = self.yaw.to_radians().cos();
self.position[0] -= forward_x * self.speed * delta_time;
self.position[2] -= forward_z * self.speed * delta_time;
```

This vector-based movement system ensures that player navigation aligns with their current orientation rather than the global coordinate axes. The calculation decomposes movement into orthogonal components along the X and Z axes.

Similar trigonometric calculations govern movement in other directions (backward, left, right), maintaining consistent spatial relationships regardless of orientation.

### Compass System

The navigational aid directs players toward the maze exit by calculating the relative angle between the player's current orientation and the exit position.

The implementation begins by establishing the player's local coordinate system:

```rust
let forward_x = player_yaw_degrees.to_radians().sin();
let forward_z = player_yaw_degrees.to_radians().cos();

let right_x = player_yaw_degrees.to_radians().cos();
let right_z = player_yaw_degrees.to_radians().sin();
```

The system then calculates a normalized direction vector to the exit and determines its projection onto the player's local coordinate axes:

```rust
let length = distance_sq.sqrt();
let dir_x = dx / length;
let dir_z = dz / length;

let forward_dot = -forward_x * dir_x - forward_z * dir_z;
let right_dot = right_x * dir_x - right_z * dir_z;
```

The final angle calculation uses the arctangent function to determine precise directional information:

```rust
let target_compass_angle = right_dot.atan2(forward_dot);
```

This solution requires similar trigonometric calculations to enable the compass to accurately point toward the exit regardless of the player's position or orientation. The mathematical approach ensures consistency with the movement system - when the compass points directly forward (0°), the player is facing precisely toward the exit.

## Coordinate System Transformations

Mirador maintains bidirectional mapping between coordinate spaces through a dedicated transformation API:

```rust
pub fn maze_to_world(cell: &Cell, maze_dimensions: (usize, usize), y_position: f32) -> [f32; 3]
pub fn world_to_maze(position: [f32; 3], maze_dimensions: (usize, usize)) -> Cell
```

The system continuously updates the player's current maze cell based on their world position:

```rust
pub fn update_cell(&mut self, maze_grid: &[Vec<bool>]) {
    let maze_dimensions = (maze_grid[0].len(), maze_grid.len());
    self.current_cell = coordinates::world_to_maze(self.position, maze_dimensions);
}
```

This continuous position tracking enables several critical game mechanics:
1. Detection of arrival at the exit cell to trigger level completion
2. Validation of player movement against wall boundaries
3. Synchronization between visual representation and logical maze state

The bidirectional system ensures that the 2D maze representation and 3D navigation space maintain perfect correspondence throughout gameplay. This coherence is fundamental to Mirador's navigational mechanics - players must locate the exit by relying on visual cues, compass guidance, and familiarity with the game mechanics. The balance between these information sources must feel rewarding to keep players engaged and motivated.

Additional transformation utilities enhance the system's capabilities:

```rust
pub fn calculate_cell_size(maze_dimensions: (usize, usize)) -> f32
pub fn get_bottom_left_cell_position(maze_dimensions: (usize, usize), y_position: f32) -> [f32; 3]
```

These functions provide consistent calculation of spatial parameters throughout the codebase, ensuring that all components interpret coordinate data identically.
