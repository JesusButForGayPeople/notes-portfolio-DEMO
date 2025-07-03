---
layout: page
title: Random Maze Generation
permalink: /maze/
---


Maze generation is a fascinating problem that sits at the intersection of graph theory, algorithms, and creative programming. This article explores a comprehensive Rust implementation that uses Kruskal's algorithm to generate random mazes, complete with visualization capabilities and file I/O operations.

## The Foundation: Graph Theory and Maze Representation

At its core, a maze is a graph where cells represent vertices and passages represent edges. The challenge lies in creating a spanning tree that connects all cells while maintaining exactly one path between any two points. This is where Kruskal's algorithm shines, as it naturally produces a minimum spanning tree from a weighted graph.

The implementation uses a clever dual-representation approach. The maze exists as a 2D grid where odd coordinates represent actual maze cells, and even coordinates represent potential walls or passages between cells. This means a 10x10 maze actually requires a 21x21 internal representation to accommodate both cells and the walls between them.

```rust
pub struct Maze {
    pub width: usize,
    pub height: usize,
    pub walls: Vec<Vec<bool>>,
    pub total_edges: usize,
    pub processed_edges: usize,
    pub exit_cell: Option<Cell>,
}
```

## Cell and Edge Abstractions

The `Cell` structure provides a clean abstraction for maze coordinates, wrapping row and column indices with useful traits for hashing and equality comparison. This simplicity is deceptive, as these cells become the vertices in our graph representation.

```rust
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Cell {
    pub row: usize,
    pub col: usize,
}
```

Edges represent potential connections between adjacent cells. During generation, these edges are shuffled randomly and processed in order, with Kruskal's algorithm determining which edges become actual passages.

```rust
#[derive(Debug, Clone, Copy)]
pub struct Edge {
    pub cell1: Cell,
    pub cell2: Cell,
}
```

## The Union-Find Data Structure

The heart of Kruskal's algorithm is the Union-Find (also known as Disjoint Set Union) data structure. This implementation uses path compression and union by rank for optimal performance, achieving nearly constant time operations for practical purposes.

```rust
pub struct UnionFind {
    parent: HashMap<Cell, Cell>,
    rank: HashMap<Cell, usize>,
}
```

The `find` operation implements path compression, flattening the tree structure as it searches for the root of a set. This optimization ensures that subsequent operations on the same elements are faster.

```rust
pub fn find(&mut self, cell: Cell) -> Cell {
    if self.parent[&cell] != cell {
        let root = self.find(self.parent[&cell]);
        self.parent.insert(cell, root);
    }
    self.parent[&cell]
}
```

The `union` operation merges two sets, using rank-based union to keep trees balanced. It returns a boolean indicating whether the union actually occurred, which is crucial for Kruskal's algorithm to know when an edge creates a new connection versus when it would create a cycle.

## Maze Generation Process

The `MazeGenerator` orchestrates the entire generation process. During initialization, it creates a Union-Find structure with all cells as separate components, generates all possible edges between adjacent cells, and shuffles them randomly.

```rust
pub struct MazeGenerator {
    pub maze: Arc<Mutex<Maze>>,
    union_find: UnionFind,
    edges: Vec<Edge>,
    current_edge: usize,
    pub generation_complete: bool,
    pub connected_cells: HashSet<Cell>,
    pub fast_threshold: usize,
    pub fast_mode: bool,
}
```

The generation process happens incrementally through the `step` method. Each step processes one edge from the shuffled list. If the edge connects two cells that are not already connected (determined by the Union-Find structure), the wall between them is removed, creating a passage.

The coordinate transformation during wall removal is particularly elegant. When connecting two cells, the wall between them is located at the average of their coordinates plus one. This works because of the dual-representation where walls exist at even coordinates between odd-coordinate cells.

```rust
if self.union_find.union(edge.cell1, edge.cell2) {
    let wall_row = edge.cell1.row + edge.cell2.row + 1;
    let wall_col = edge.cell1.col + edge.cell2.col + 1;
    maze.walls[wall_row][wall_col] = false;

    self.connected_cells.insert(edge.cell1);
    self.connected_cells.insert(edge.cell2);
    return true;
}
```

## Visualization and Rendering

The maze supports real-time visualization through pixel-based rendering. The `get_render_data` method converts the internal wall representation into RGBA pixel data, with different colors representing walls, passages, connected cells, and exit points.

The rendering system uses a fixed cell size (4 pixels) and wall thickness (1 pixel), creating a clear visual distinction between different maze elements. Connected cells are rendered in white, walls in black, and the exit cell in red when present. (For more information on the rendering see the [Rendering Pipelines](/renderer/))

<div class="centered-video">
    <video controls width="800" autoplay loop muted playsinline>
        <source src="/assets/maze.mp4" type="video/mp4">
            Your browser does not support the video tag.
    </video>
</div>



The implementation includes a "fast mode" that kicks in when fewer than 600 edges remain unprocessed. This optimization recognizes that toward the end of generation, most edges will be rejected because they would create cycles, so the visualization can be updated less frequently without losing the essential character of the generation process.

## File I/O and Persistence

The maze can be saved to disk using a simple text format where `#` represents walls, spaces represent passages, and `*` marks the exit cell. The file naming uses timestamps to ensure uniqueness, and the directory structure is automatically created if it doesn't exist.

```rust
pub fn save_to_file(&self) -> Result<PathBuf, std::io::Error> {
    let timestamp = Local::now().format("Maze_%m-%d-%y_%I-%M%p.mz").to_string();
    let output_path = Path::new("src/maze/saved-mazes/generated").join(timestamp);

    // File creation and writing logic...
}
```

The parsing functionality reverses this process, reading maze files and reconstructing the internal wall representation. This allows for loading and manipulating previously generated mazes.

## Pathfinding Support

The implementation includes methods like `is_walkable` and `is_wall` that convert between the user-friendly coordinate system and the internal representation. These methods are essential for pathfinding algorithms that might operate on the generated mazes.

```rust
pub fn is_walkable(&self, x: usize, y: usize) -> bool {
    if x >= self.width || y >= self.height {
        return false;
    }

    let wall_row = y * 2 + 1;
    let wall_col = x * 2 + 1;

    if wall_row >= self.walls.len() || wall_col >= self.walls[0].len() {
        return false;
    }

    !self.walls[wall_row][wall_col]
}
```

## Closing Notes

The use of `Arc<Mutex<Maze>>` enables safe concurrent access to the maze during generation. This design allows for real-time visualization while generation is occurring, or for multiple threads to safely read the maze state without data races.

Kruskal's algorithm guarantees that the resulting maze will be a spanning tree, meaning every cell is reachable from every other cell through exactly one path. This property is essential for a proper maze, as it ensures both solvability and uniqueness of solutions.

The random shuffling of edges before processing ensures that each generation produces a different maze layout, while the Union-Find structure guarantees that no cycles are created, maintaining the tree property throughout the generation process.
