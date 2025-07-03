---
layout: post
title: Coordinates
---

Sure! Here's your content converted into a properly structured Markdown document with embedded Rust code blocks where appropriate:


## 1. Maze Grid Coordinate System

This is a 2D coordinate system used for maze generation and pathfinding.

- `row` and `col` indicate cell positions in the maze.
- `(0, 0)` is at the **top-left** corner of the maze.
- The maze is represented by a 2D boolean array:
  - `true` represents a **wall**
  - `false` represents a **path**

Each cell is represented by a `Cell` struct:

```rust
struct Cell {
    row: usize,
    col: usize,
}
````

---

## 2. World Coordinate System (3D)

This is the 3D coordinate system used for rendering and physics:

* `[x, y, z]` where:

  * `x`: left/right
  * `y`: up/down
  * `z`: forward/backward

### Characteristics

* The origin `[0.0, 0.0, 0.0]` is at the **center of the floor**
* Positive **Y is upward**
* The system uses a **right-handed coordinate system**

As defined in `math/vec.rs`.

---

## 3. Grid-to-World Mapping

The maze grid is mapped into the 3D world with the following transformations:

* The entire floor is `3000.0 x 3000.0` world units
* The maze is centered on the origin
* **Cell size** is computed as:

```rust
let cell_size = floor_size / max(maze_width, maze_height) as f32;
```

* **Origin offset** for the maze is:

```rust
let origin_x = -(maze_width as f32 * cell_size) / 2.0;
let origin_z = -(maze_height as f32 * cell_size) / 2.0;
```

---

## 4. Player Position and Starting Cell

The player’s position is defined in `player.rs`:

```rust
position: [1475.0, 50.0, 1475.0]
```

This places the player:

* In the **positive XZ quadrant**
* Slightly elevated at `y = 50`

---

## 5. Mapping Player Position to Maze Cell

To determine which maze cell the player is currently in, the following method is used:

```rust
pub fn update_cell(&mut self, maze_grid: &[Vec<bool>]) {
    let floor_size = 3000.0;
    let maze_width = maze_grid[0].len();
    let maze_height = maze_grid.len();

    // Calculate cell size to match wall generation logic
    let max_dimension = maze_width.max(maze_height) as f32;
    let cell_size = floor_size / max_dimension;
    let half_maze = 1500.0;

    let x = ((self.position[0] + half_maze) / cell_size).floor() as i32;
    let z = ((self.position[2] + half_maze) / cell_size).floor() as i32;

    self.current_cell = Cell {
        row: z as usize,
        col: x as usize,
    };
}
```

This converts the player's 3D world position into the appropriate `Cell { row, col }` within the maze grid.
