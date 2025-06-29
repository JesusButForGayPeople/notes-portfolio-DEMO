---
layout: page
title: App State Management
permalink: /app/
---

## Overview

Mirador follows a hierarchical architecture where the `App` struct serves as the top-level container for the entire program, while `AppState` contains the operational components including rendering pipelines, game logic, and user interface systems.

## Core Structures

### App - Top Level Application Container

The `App` struct is the **top-level struct of the entire program** and serves as the main application object for Mirador. It manages the fundamental WGPU instance, window system integration, and implements the event-driven architecture through `winit::application::ApplicationHandler`.

```rust
#[derive(Default)]
pub struct App {
    instance: wgpu::Instance,
    state: Option<AppState>,
    window: Option<Arc<Window>>,
}
```
{: .language-rust}

#### Key Responsibilities:
- **WGPU Instance Management**: Maintains the core WebGPU instance for all graphics operations
- **Window Lifecycle**: Handles window creation, management, and cleanup
- **Event Processing**: Implements the winit event loop for cross-platform input and system events
- **State Container**: Holds the optional `AppState` which contains all operational components

### AppState - Application Core

The `AppState` struct **contains the meat of the application** including the various rendering pipelines, the game state, and all UI elements. This is where all the active components of a running game session reside.

```rust
pub struct AppState {
    wgpu_renderer: WgpuRenderer,
    egui_renderer: EguiRenderer,
    ui: UiState,
    game_state: GameState,
    key_state: KeyState,
}
```
{: .language-rust}

#### Key Components:

**Rendering Pipelines:**
- **`wgpu_renderer`**: Handles all 3D graphics rendering including the maze geometry, starfield backgrounds, maze animations, and depth-tested 3D scenes. \[See [**renderer**](/renderer/) for more information.  \]
- **`egui_renderer`**: Manages the immediate-mode GUI system for all user interface overlays, menus, and debug panels. \[See [**User Interface (egui)**](/ui/) for more information.  \]

**Application State:**
- **`ui`**: Contains all UI component states including sliders, color pickers, configuration panels, and user preferences
- **`game_state`**: Encapsulates the core game logic including player position/orientation, maze data, timing systems, and game progression
- **`key_state`**: Tracks current input state including pressed keys, mouse position, and input event handling

## Architecture Flow

The application follows this initialization and operation flow:

1. **`App` Creation**: The top-level `App` struct is instantiated with default values
2. **WGPU Initialization**: The WGPU instance is created for graphics device management
3. **Window Setup**: The application window is created and configured
4. **`AppState` Initialization**: All rendering pipelines, game systems, and UI components are initialized
5. **Event Loop**: The winit event loop processes input, updates game state, and triggers rendering

This separation allows for clean resource management where the `App` handles system-level concerns while `AppState` focuses on application-specific functionality.
