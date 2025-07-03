---
layout: page
title: Math Utilities
permalink: /math/
---


When building 3D graphics applications, particularly when interfacing with GPU APIs like WGPU or OpenGL, having robust mathematical utilities is essential. This article examines the math utilities used by Mirador, covering matrix operations, vector mathematics, and coordinate system transformations specifically tailored for maze-based applications.

## The Foundation: Memory Layout and GPU Compatibility

The mathematical structures in this codebase are designed with GPU compatibility as a primary concern. The `Mat4` struct uses the `#[repr(transparent)]` attribute and implements `bytemuck::Pod` and `bytemuck::Zeroable` traits, ensuring that the memory layout is predictable and can be safely transmitted to GPU buffers.

<span class="highlight-green">The matrix storage follows column-major ordering</span>, which aligns with WGSL (WebGPU Shading Language) expectations. This means that what might intuitively be thought of as the first row is actually stored as the first column in memory:

```rust
Mat4([
    [m00, m10, m20, m30],  // First column
    [m01, m11, m21, m31],  // Second column
    [m02, m12, m22, m32],  // Third column
    [m03, m13, m23, m33],  // Fourth column
])
```

## Matrix Operations and Transformations

### Basic Matrix Construction

The `Mat4` implementation provides several fundamental matrix constructors. The identity matrix serves as the mathematical neutral element for matrix multiplication:

```rust
Mat4([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0],
])
```

### Projection Matrices

The codebase implements both orthographic and perspective projection matrices, which are fundamental for 3D rendering pipelines.

#### Orthographic Projection

The orthographic projection creates a parallel projection where objects maintain their size regardless of distance from the camera. The implementation maps a 3D rectangular region to the normalized device coordinate space:

```rust
Mat4([
    [2.0 / (right - left), 0.0, 0.0, 0.0],
    [0.0, 2.0 / (top - bottom), 0.0, 0.0],
    [0.0, 0.0, 1.0 / (near - far), 0.0],
    [
        (right + left) / (left - right),
        (top + bottom) / (bottom - top),
        near / (near - far),
        1.0,
    ],
])
```

The scaling factors `2.0 / (right - left)` and `2.0 / (top - bottom)` normalize the x and y coordinates to the range [-1, 1]. The z-coordinate scaling `1.0 / (near - far)` maps the depth range, while the translation components center the projection volume at the origin.

#### Perspective Projection

The perspective projection creates a more realistic view where distant objects appear smaller. The implementation uses the field of view approach:

```rust
let f = 1.0 / (field_of_view_y_in_radians * 0.5).tan();
let range_reciprocal = 1.0 / (z_near - z_far);

Mat4([
    [f / aspect, 0.0, 0.0, 0.0],
    [0.0, f, 0.0, 0.0],
    [0.0, 0.0, z_far * range_reciprocal, -1.0],
    [0.0, 0.0, z_far * z_near * range_reciprocal, 0.0],
])
```

The focal length `f` is calculated from the field of view, and the aspect ratio correction ensures that the projection maintains proper proportions across different screen dimensions. The depth mapping follows OpenGL conventions with a range from -1 to 1.

### Transformation Matrices

#### Translation

Translation matrices move objects in 3D space without changing their orientation or scale. The implementation places the translation values in the fourth column:

```rust
Mat4([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [tx, ty, tz, 1.0],
])
```

#### Scaling

Scaling matrices modify the size of objects along each axis. The scaling factors are placed along the main diagonal:

```rust
Mat4([
    [sx, 0.0, 0.0, 0.0],
    [0.0, sy, 0.0, 0.0],
    [0.0, 0.0, sz, 0.0],
    [0.0, 0.0, 0.0, 1.0],
])
```

#### Rotation

The rotation matrices implement rotations around each primary axis using trigonometric functions. Each rotation follows the right-hand rule, where positive angles represent counter-clockwise rotation when viewed from the positive axis direction.

For X-axis rotation:

```rust
let c = (deg_to_rad(angle_in_radians)).cos();
let s = (deg_to_rad(angle_in_radians)).sin();
Mat4([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, c, -s, 0.0],
    [0.0, s, c, 0.0],
    [0.0, 0.0, 0.0, 1.0],
])
```

The Y-axis and Z-axis rotations follow similar patterns but with the trigonometric values positioned differently to affect the appropriate coordinate planes.

### Matrix Multiplication and Inversion

The matrix multiplication implementation uses the standard algorithm where each element of the result matrix is computed as the dot product of the corresponding row and column:

```rust
for (i, row) in result.iter_mut().enumerate() {
    for (j, cell) in row.iter_mut().enumerate() {
        *cell = (0..4).map(|k| b.0[i][k] * self.0[k][j]).sum();
    }
}
```

The matrix inversion is optimized specifically for affine transformations, which are common in 3D graphics. The method extracts the 3x3 linear transformation part and the translation vector, then computes the inverse using the determinant and adjugate matrix approach. This optimization is valid because most graphics transformations preserve the affine structure where the last row remains [0, 0, 0, 1].

## Vector Mathematics

### Vector Structure and Operations

The `Vec3` struct represents 3D vectors with similar GPU-compatible memory layout considerations. The implementation provides essential vector operations including dot product, cross product, normalization, and length calculation.

#### Dot Product

The dot product implementation follows the standard mathematical definition:

```rust
self.x() * other.x() + self.y() * other.y() + self.z() * other.z()
```

This operation is fundamental for calculating angles between vectors, projections, and lighting calculations in graphics programming.

#### Cross Product

The cross product creates a vector perpendicular to both input vectors, following the right-hand rule:

```rust
Vec3([
    self.y() * other.z() - self.z() * other.y(),
    self.z() * other.x() - self.x() * other.z(),
    self.x() * other.y() - self.y() * other.x(),
])
```

This operation is essential for calculating surface normals, creating coordinate systems, and determining the orientation of three points in space.

#### Normalization

Vector normalization converts a vector to unit length while preserving its direction. The implementation includes safety checks for zero-length vectors:

```rust
let length = self.length();
if length <= f32::EPSILON {
    return Self([0.0, 0.0, 0.0]);
}
Self([self.x() / length, self.y() / length, self.z() / length])
```

## Coordinate System Transformations

### Maze-to-World Coordinate Mapping

The coordinate transformation system bridges the gap between discrete maze grid coordinates and continuous 3D world coordinates. The transformation accounts for maze centering and proper scaling.

The core transformation calculates the world position by first determining the cell size based on the largest maze dimension:

```rust
let max_dimension = maze_width.max(maze_height) as f32;
let cell_size = FLOOR_SIZE / max_dimension;
```

This approach ensures that the maze fits within a predefined floor size regardless of its actual grid dimensions. The origin offset centers the maze in world space:

```rust
let origin_x = -(maze_width as f32 * cell_size) / 2.0;
let origin_z = -(maze_height as f32 * cell_size) / 2.0;
```

The final world coordinates place each cell at its center rather than at grid intersections:

```rust
let world_x = origin_x + (cell.col as f32 + 0.5) * cell_size;
let world_z = origin_z + (cell.row as f32 + 0.5) * cell_size;
```

### World-to-Maze Coordinate Mapping

The inverse transformation converts world coordinates back to maze grid cells. This is essential for collision detection, pathfinding, and game logic that needs to determine which maze cell corresponds to a given world position.

The implementation reverses the transformation process:

```rust
let relative_x = position[0] - origin_x;
let relative_z = position[2] - origin_z;

let col = (relative_x / cell_size).floor() as usize;
let row = (relative_z / cell_size).floor() as usize;
```

Boundary clamping ensures that world positions outside the maze bounds are mapped to the nearest valid cell:

```rust
let col = col.min(maze_width - 1);
let row = row.min(maze_height - 1);
```

## Directional Navigation and Positioning

### Cardinal Direction System

The direction system provides a clean abstraction for maze navigation. The `Direction` enum represents the four cardinal directions, and the conversion functions bridge between different representations of orientation.

#### Yaw-to-Direction Conversion

The yaw angle conversion normalizes arbitrary rotation angles to the 0-360 degree range and maps them to cardinal directions:

```rust
let normalized_yaw = ((yaw % 360.0) + 360.0) % 360.0;

match normalized_yaw as u32 {
    315..=359 | 0..=45 => Direction::North,
    46..=135 => Direction::East,
    136..=225 => Direction::South,
    226..=314 => Direction::West,
    _ => Direction::North,
}
```

This approach provides 90-degree sectors for each cardinal direction, with North covering both the 315-360 and 0-45 degree ranges to handle the wraparound at 0/360 degrees.

#### Cell-to-Cell Direction Calculation

The system can determine the primary direction between any two cells by comparing the magnitude of row and column differences:

```rust
let row_diff = to.row as isize - from.row as isize;
let col_diff = to.col as isize - from.col as isize;

if row_diff.abs() > col_diff.abs() {
    if row_diff < 0 {
        Some(Direction::North)
    } else {
        Some(Direction::South)
    }
} else if col_diff.abs() > row_diff.abs() {
    if col_diff > 0 {
        Some(Direction::East)
    } else {
        Some(Direction::West)
    }
} else {
    None
}
```

This implementation prioritizes the axis with the larger displacement, returning `None` for diagonal or identical positions where no clear cardinal direction applies.

### Boundary and Corner Detection

The positioning utilities provide functions to identify specific maze locations such as corners and boundaries. These functions are particularly useful for maze generation algorithms, spawn point determination, and navigation logic.

The corner detection functions follow a consistent pattern, calculating positions based on maze dimensions:

```rust
fn get_bottom_right_cell(maze_dimensions: (usize, usize)) -> Cell {
    let (maze_width, maze_height) = maze_dimensions;
    Cell::new(maze_height - 1, maze_width - 1)
}
```

### Adjacent Cell Navigation

The adjacent cell calculation provides safe navigation within maze boundaries:

```rust
match direction {
    Direction::North if row > 0 => Some(Cell::new(row - 1, col)),
    Direction::South if row < maze_height - 1 => Some(Cell::new(row + 1, col)),
    Direction::East if col < maze_width - 1 => Some(Cell::new(row, col + 1)),
    Direction::West if col > 0 => Some(Cell::new(row, col - 1)),
    _ => None,
}
```

This implementation combines direction-specific movement with boundary checking, returning `None` for movements that would exceed maze boundaries rather than panicking or producing invalid coordinates.

## Practical Applications and Integration

These mathematical utilities form the foundation for a complete 3D maze navigation system. The matrix operations handle camera transformations and rendering pipeline setup, while the vector mathematics supports lighting calculations, collision detection, and physics simulations.

The coordinate transformation system enables seamless integration between game logic that operates on discrete maze cells and rendering systems that work with continuous world coordinates. This separation of concerns allows for clean code organization where maze generation algorithms can work with simple grid coordinates while rendering and physics systems operate in proper 3D space.

The directional navigation system provides the necessary abstractions for implementing maze-solving algorithms, player movement controls, and AI pathfinding. By standardizing on cardinal directions and providing robust conversion functions, the system supports various input methods while maintaining consistent internal representation.

This mathematical foundation demonstrates how careful attention to memory layout, coordinate system conventions, and API design can create utilities that are both mathematically correct and practically useful for real-world graphics programming applications.
