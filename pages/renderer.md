---
layout: page
title: Rendering Pipelines
permalink: /renderer/
---

## Overview

All rendering in Mirador is orchestrated by the `WgpuRenderer` struct, which encapsulates the GPU device, surface, and all rendering pipelines. The rendering system is modular, with specialized sub-renderers for different aspects of the game, such as the main 3D maze, animated backgrounds, and loading or transition effects. As you can see below, the different renderers are nested within one another. Each subsequent renderer handles a more specific component of rendering the scenes in which they are needed.

## Core Structure

<embed src="{{ site.baseurl }}/assets/Renderers-Diagram.pdf" type="application/pdf" width="100%" height="1250px" />

## Rendering Flow

Each frame, the rendering process follows this sequence:

1. **State Update**: Game and animation state are updated based on input and timing.
2. **Pipeline Selection**: Depending on the game state (e.g., gameplay, loading), either `game_renderer` or `animation_renderer` is used.
3. **Scene Rendering**: The selected renderer draws its components to the frame buffer, including the maze, background, and any overlays or effects.
4. **Presentation**: The composed frame is presented to the window surface.

---


This architecture allows for clear separation between gameplay rendering and animated sequences, while sharing GPU resources efficiently.


### WgpuRenderer – Central Rendering Manager

The `WgpuRenderer` struct is the central hub for all GPU-based rendering in Mirador. It manages the WGPU device and queue, the window surface, and contains the main rendering pipelines for both the game and animation sequences. It contains two sub-renderers: `GameRenderer` which handles the 3D maze rendering, and `AnimationRenderer` which handles the 2D maze rendering. They each contain their own set of sub-renderers for additional effects.

```rust
pub struct WgpuRenderer {
    pub surface: wgpu::Surface<'static>,
    pub surface_config: wgpu::SurfaceConfiguration,
    pub device: wgpu::Device,
    pub queue: wgpu::Queue,
    pub game_renderer: GameRenderer,
    pub animation_renderer: AnimationRenderer,
}
```
{: .language-rust}

#### Key Responsibilities:
- **Surface and Device Management**: Handles the GPU device, command queue, and presentation surface.
- **Pipeline Initialization**: Sets up and manages all rendering pipelines used throughout the game.
- **Delegation**: Delegates actual drawing to specialized sub-renderers for different visual components.

---

### GameRenderer – Main 3D Maze and Scene Pipeline

The `GameRenderer` struct is responsible for rendering the core 3D maze, floor, and background effects during gameplay. It manages the main render pipeline, vertex and uniform buffers, and several sub-renderers for additional effects. The two sub renderers contained within, `StarRenderer` and `DebugRenderer`, handle the rendering of the stars in the background, and the rendering of the bounding boxes for debugging purposes respectively.

```
pub struct GameRenderer {
    pub pipeline: wgpu::RenderPipeline,
    pub vertex_buffer: wgpu::Buffer,
    pub vertex_count: u32,
    pub uniform_buffer: wgpu::Buffer,
    pub uniform_bind_group: wgpu::BindGroup,
    pub depth_texture: Option<wgpu::Texture>,
    pub star_renderer: StarRenderer,
    pub debug_renderer: DebugRenderer,
}
```
{: .language-rust}

#### Fields:
- **pipeline**: The main WGPU render pipeline for the maze and floor geometry.
- **vertex_buffer**: Combined buffer for all maze and floor vertices.
- **vertex_count**: Number of vertices in the vertex buffer.
- **uniform_buffer**: Store the transformation matrices for the shaders.
- **uniform_bind_group**: Store and bind transformation matrices for the shaders.
- **depth_texture**: Depth buffer for correct 3D occlusion, optional due to absence on initialization.
- **star_renderer**: Renders animated starfield backgrounds.
- **debug_renderer**: Provides tools for visualizing bounding boxes and debug overlays.

---

### AnimationRenderer – Title Screen and Transition Effects

The `AnimationRenderer` struct is dedicated to rendering animated sequences, such as the title screen maze, loading bars, and special exit effects. It combines maze generation logic with specialized sub-renderers for each visual element.

```rust
pub struct AnimationRenderer {
    pub generator: MazeGenerator,
    pub maze: Arc<Mutex<Maze>>,
    pub maze_renderer: MazeRenderer,
    pub loading_bar_renderer: LoadingBarRenderer,
    pub exit_shader_renderer: ExitShaderRenderer,
    pub texture: wgpu::Texture,
    pub last_update: Instant,
}
```
{: .language-rust}

#### Fields:
- **generator**: Includes all the information from generating the maze structure.
- **maze**: Stores the maze data including walls and its exit.
- **maze_renderer**: Renders the animated maze during title or transition screens.
- **loading_bar_renderer**: Displays loading progress with a visual bar.
- **exit_shader_renderer**: Creates animated effects for the maze exit.
- **texture**: Stores the maze image as a GPU texture.
- **last_update**: Tracks timing for smooth animation.
