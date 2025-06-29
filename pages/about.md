---
layout: page
title: About
permalink: /about/
---

<p class="dictionary-entry">
  <strong class="entry-word">mirador</strong>
  <span class="part-of-speech">noun</span><br />
  <span class="phonetic">/ˈmir-ə-ˌdȯr/, or /ˌmir-ə-ˈdȯr/</span><br />
  <span class="definition">a turret, window, or balcony designed to command an extensive outlook</span>
</p>

**Mirador** is a modular, interactive application written in Rust, focused on real-time rendering, procedural maze generation, and game-like user interaction. It leverages modern GPU technologies and immediate-mode GUI frameworks to provide a responsive and visually engaging experience.

---

## Purpose

Mirador is a work in progress game engine written entirely in Rust. It is designed to be modular, real-time, and memory-efficient. It achieves this by employing several rendering pipelines that each handle specific aspects of the game's visual and interactive elements, all of which leverage the computational power of the GPU via the WGPU graphics API. Whilst this project is still in its infancy, it currently supports:

- Real-time rendering using the WGPU graphics API.
- Integration with egui for overlays, controls, and interactive panels.
- Modular architecture for game state, rendering, and UI.
- Procedural maze generation and animation.
- Responsive input handling and event-driven updates.


## Architecture Overview

Mirador is organized into several core modules:

- [**App**](/app/): The main application object, responsible for initialization, event handling, rendering, and orchestrating the game state.
- [**Game**](/game/): Contains logic for player state, input handling, and core gameplay mechanics.
- [**Maze**](/maze/): Handles procedural maze generation, storage, and rendering data.
- [**Rendering**](/renderer/): Manages all rendering pipelines.
- [**UI**](/ui/): Implements egui-based overlays for easier development and debugging.
- [**Math**](/math/): Provides vector and matrix utilities for graphics and game logic.

The application initializes a WGPU instance and event loop, sets up rendering and UI pipelines, and manages all state transitions and user interactions through a central `App` struct.

---

## Technologies Used

- **Rust** (edition 2024)
- **WGPU**: Modern, portable graphics API for GPU rendering.
- **egui**: Immediate-mode GUI library for Rust.
- **winit**: Cross-platform window and event loop management.
- **rand**: Random number generation for procedural content.
- **chrono**: Time and date utilities.

---

## Getting Started

Mirador is intended for developers and enthusiasts interested in graphics programming, game development, or Rust-based application architecture. To explore or contribute:

1. Ensure you have a recent Rust toolchain installed.
2. Clone the repository and build with `cargo build`.
3. Run the application with `cargo run`.

---

## License

Mirador is released under an open-source license. See the repository for details.
