---
layout: post
title: Coordinate Systems in Mirador
---

## 1. Maze Grid Coordinate System

This grid system provides a wrapper where:
- Grid positions are indexed by `row` and `col` parameters
- The origin `(0, 0)` is established at the top-left corner
- The maze structure is represented in a 2D boolean array where:
  - `true` values designate impassable walls
  - `false` values designate navigable pathways

The implementation utilizes a `Cell` struct to encapsulate maze positions:

```rust
struct Cell {
    row: usize,
    col: usize,
}
```

In Mirador's implementation, the maze entry point is situated at the bottom-left cell, expressed as `(height-1, 0)` in grid coordinates. This position functions as the player's starting location. The exit cell is  placed during maze generation and marked with an asterisk character (`*`) in serialized maze files.

## 2. World Coordinate System (3D)

To create an immersive navigation experience, Mirador translates the 2D maze representation into a 3D world coordinate system that handles both rendering and collision physics calculations; this is the world that the player spends most of their time in.

This 3D system employs a position vector `[x, y, z]` where:
* `x`: represents horizontal position (positive = east/right)
* `y`: represents vertical elevation (positive = up)
* `z`: represents depth (positive = south/backward)

Critical characteristics of this system include:
* Origin placement at `[0.0, 0.0, 0.0]` (center of the floor)
* Implementation of a standard right-handed coordinate system
* Integration with rendering pipelines through `math/vec.rs`

## 3. Grid-to-World Mapping

The transformation between grid and world coordinates requires is achieved via the following approach to mapping:

* The game floor spans `FLOOR_SIZE = 3000.0` world units square
* The maze is centered at the world origin to maximize available space
* Individual cell size is dynamically calculated based on maze dimensions:

```rust
let cell_size = floor_size / max(maze_width, maze_height) as f32;
```

This adaptive scaling ensures that mazes of varying dimensions fit proportionally within the constrained floor space. The calculation maintains consistent cell size.

The system determines precise world coordinates by calculating offsets from the origin:

```rust
let origin_x = -(maze_width as f32 * cell_size) / 2.0;
let origin_z = -(maze_height as f32 * cell_size) / 2.0;
```


## 4. Player Position and Starting Cell

Mirador's player positioning system employs coordinate transformation to place the player at the maze entrance. When a new level is initialized, the following function positions the player appropriately:

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

## 5. Direction and Orientation

### Player Movement

Mirador implements player movement through trigonometric calculations that translate user input into movement delta vectors. This approach creates intuitive navigation that responds correctly to the player's current orientation and appropriately handle 3D projection:

```rust
let forward_x = self.yaw.to_radians().sin();
let forward_z = self.yaw.to_radians().cos();
self.position[0] -= forward_x * self.speed * delta_time;
self.position[2] -= forward_z * self.speed * delta_time;
```

This vector-based movement system ensures that player navigation aligns with their current orientation rather than the global coordinate axes. The calculation decomposes movement into orthogonal components along the X and Z axes. By applying trig functions to the yaw angle, the system determines the appropriate direction vector that corresponds to the *player's* "forward" direction.

Similar trig calculations govern movement in other directions (backward, left, right), maintaining consistent spatial relationships regardless of orientation.

### Compass System

This navigational aid directs players toward the maze exit by calculating the relative angle between the player's current orientation and the exit position.

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

The final angle calculation employs the arctangent function to determine precise directional information:

```rust
let target_compass_angle = right_dot.atan2(forward_dot);
```

This solution demands similar trig calculations to enable the compass to accurately point toward the exit regardless of the player's position or orientation. The mathematical approach ensures consistency with the movement system—when the compass points directly forward (0°), the player is facing precisely toward the exit.

## 6. Coordinate System Transformations

Mirador maintains bidirectional mapping between coordinate spaces through a dedicated transformation API (we will see how long it lasts):

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

The bidirectional system ensures that the 2D maze representation and 3D navigation space maintain perfect correspondence throughout gameplay, which was an issue up until now. This coherence is fundamental to Mirador's navigational mechanics,in order to keep the game interesting the player must locate the exit by relying on both visual cues, the compass guidance system, as well as overall familiarity with the mechanics of the game. I need to make sure that the balance between these sources feels rewarding in order to keep the player engaged and motivated to continue playing.

Additional transformation utilities further enhance the system's capabilities:

```rust
pub fn calculate_cell_size(maze_dimensions: (usize, usize)) -> f32
pub fn get_bottom_left_cell_position(maze_dimensions: (usize, usize), y_position: f32) -> [f32; 3]
```

These functions provide consistent calculation of spatial parameters throughout the codebase, ensuring that all components of the game engine interpret coordinate data identically.
