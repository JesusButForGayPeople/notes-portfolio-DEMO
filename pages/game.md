---
layout: page
title: Game State Management
permalink: /game/
---

## Overview

The game module serves as the core gameplay system within Mirador, implementing a first-person maze navigation experience. The architecture follows a clean separation of concerns with three primary components: input handling, player management, and centralized game state coordination. This module provides collision detection, movement mechanics, and game progression tracking through a maze-based gameplay loop.

## Core Structures

### GameState - Central Game Coordinator

The `GameState` struct serves as the **central hub for all mutable game data** and coordinates between different game systems. It maintains the game loop timing, player state, UI management, and level progression.

```rust
#[derive(Debug, Clone)]
pub struct GameState {
    pub player: Player,
    pub last_frame_time: Instant,
    pub delta_time: f32,
    pub frame_count: u32,
    pub current_fps: u32,
    pub last_fps_time: Instant,
    pub title_screen: bool,
    pub maze_path: Option<PathBuf>,
    pub capture_mouse: bool,
    pub collision_system: CollisionSystem,
    pub level: u32,
    pub exit_reached: bool,
    pub exit_cell: Cell,
}
```

#### Field Explanations:
- **player**: The player character containing position, orientation, and movement parameters
- **last_frame_time**: Timestamp of the previous frame for delta time calculation
- **delta_time**: Time elapsed since last frame in seconds, used for frame-rate independent movement
- **frame_count**: Total number of rendered frames since game start
- **current_fps**: Current frames per second for performance monitoring
- **last_fps_time**: Timestamp of last FPS calculation update
- **title_screen**: Boolean flag controlling whether the title screen overlay is displayed
- **maze_path**: Optional file path to the currently loaded maze definition
- **capture_mouse**: Controls whether mouse input is captured for camera movement
- **collision_system**: Handles collision detection between player and maze geometry
- **level**: Current level number for progression tracking
- **exit_reached**: Flag indicating whether the player has reached the maze exit
- **exit_cell**: Coordinates of the maze exit cell

### Player - Character State and Movement

The `Player` struct encapsulates all aspects of the player character including spatial positioning, camera orientation, and movement mechanics for the first-person perspective.

```rust
#[derive(Debug, Default, Clone)]
pub struct Player {
    pub position: [f32; 3],
    pub pitch: f32,
    pub yaw: f32,
    pub fov: f32,
    pub base_speed: f32,
    pub speed: f32,
    pub mouse_sensitivity: f32,
    pub current_cell: Cell,
}
```

#### Field Explanations:
- **position**: World-space coordinates `[x, y, z]` of the player's location
- **pitch**: Vertical camera rotation in degrees (up/down looking)
- **yaw**: Horizontal camera rotation in degrees (left/right turning)
- **fov**: Field of view angle in degrees for camera projection
- **base_speed**: Default movement speed in units per second
- **speed**: Current movement speed, modified by sprint and other factors
- **mouse_sensitivity**: Multiplier for mouse movement to camera rotation conversion
- **current_cell**: Grid coordinates of the maze cell the player currently occupies

### Input Abstraction System

#### GameKey - Action Abstraction

The `GameKey` enum provides a **hardware-agnostic input abstraction layer** that decouples game actions from specific physical input devices.

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum GameKey {
    MouseButtonLeft,
    MouseButtonRight,
    MoveForward,
    MoveBackward,
    MoveLeft,
    MoveRight,
    Sprint,
    Jump,
    ToggleSliders,
    Quit,
    Escape,
    ToggleBoundingBoxes,
}
```

#### KeyState - Input State Management

The `KeyState` struct tracks which game actions are currently active and applies them to the game state each frame.

```rust
#[derive(Debug, Default)]
pub struct KeyState {
    pub pressed_keys: HashSet<GameKey>,
}
```

#### Field Explanations:
- **pressed_keys**: Hash set containing all currently pressed game keys for efficient lookup and state tracking

## Key Responsibilities

### Input Processing and Mapping
- **Hardware Abstraction**: Maps physical keyboard and mouse inputs to logical game actions through the `GameKey` enum
- **State Tracking**: Maintains which actions are currently active using efficient hash set storage
- **Flexible Mapping**: Supports multiple physical keys mapping to the same action (WASD and arrow keys for movement)
- **Input Translation**: Converts winit keyboard events to game actions through dedicated mapping functions

### Player Movement and Camera Control
- **First-Person Movement**: Implements standard FPS-style movement with forward/backward/strafe mechanics
- **Camera Orientation**: Handles pitch and yaw rotation based on mouse input with pitch clamping to prevent camera flip
- **Speed Modulation**: Supports sprint functionality that dynamically adjusts movement speed
- **Collision-Aware Movement**: Integrates with collision system to prevent clipping through maze walls
- **View Matrix Generation**: Computes camera transformation matrices for rendering pipeline

### Game State Coordination
- **Frame Timing**: Manages delta time calculation for frame-rate independent updates
- **Performance Monitoring**: Tracks and calculates frames per second for performance analysis
- **UI State Management**: Controls title screen display and mouse capture states
- **Level Progression**: Manages current level, exit detection, and progression mechanics
- **Maze Integration**: Tracks player position within maze grid coordinates for collision and logic purposes

### Collision Detection
- **Spatial Awareness**: Maintains collision system with configurable player radius and height
- **Movement Validation**: Ensures player movement respects maze geometry boundaries
- **Cell Tracking**: Updates player's current maze cell based on world position for efficient spatial queries

For more information on collision detection with bounding volume hierarchies, please refer to the [Collision Detection with Bounding Volume Hierarchies](/collision/) page.
