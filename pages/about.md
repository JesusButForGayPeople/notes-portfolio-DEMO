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

**Mirador** is a modular, interactive game written in Rust, focused on real-time rendering, procedural maze generation, and immersive gameplay. It leverages modern GPU technologies and custom UI systems to provide a responsive and visually engaging experience.

---

## Purpose

Mirador is a work in progress stealth game written entirely in Rust. It is designed to be modular, real-time, and memory-efficient. It achieves this by employing several rendering pipelines that each handle specific aspects of the game's visual and interactive elements, all of which leverage the computational power of the GPU via the WGPU graphics API. Whilst this project is still in development, it currently supports:

- Real-time rendering using the WGPU graphics API.
- Custom UI system with responsive buttons, menus, and interactive panels.
- Modular architecture for game state, rendering, and UI.
- Procedural maze generation and animation.
- Responsive input handling and event-driven updates.
- Audio system with spatial sound and music integration.
- Upgrade system with collectible power-ups and progression.
- Enemy AI with pathfinding and detection mechanics.


## Architecture Overview

Mirador is organized into several core modules:

- [**App**](/app/): The main application object, responsible for initialization, event handling, rendering, and orchestrating the game state.
- [**Game**](/game/): Contains logic for player state, input handling, core gameplay mechanics, audio, and upgrade systems.
- [**Maze**](/maze/): Handles procedural maze generation, storage, and rendering data.
- [**Rendering**](/renderer/): Manages all rendering pipelines including custom UI, text, and graphics.
- [**UI**](/ui/): Implements custom UI system with buttons, menus, and interactive elements.
- [**Math**](/math/): Provides vector and matrix utilities for graphics and game logic.

The application initializes a WGPU instance and event loop, sets up rendering and UI pipelines, and manages all state transitions and user interactions through a central `App` struct.

---

## Technologies Used

- [**Rust**](https://www.rust-lang.org/) : (edition 2024)
- [**WGPU**](https://wgpu.rs): Modern, portable graphics API for GPU rendering.
- [**winit**](https://github.com/rust-windowing/winit): Cross-platform window and event loop management.
- [**rand**](https://github.com/rust-random/rand): Random number generation for procedural content.
- [**chrono**](https://github.com/chronotope/chrono): Time and date utilities.
- [**glyphon**](https://github.com/grovesNL/glyphon): Modern rust API for rendering text on the GPU via wgpu.
- [**kira**](https://github.com/tesselode/kira): Audio library for sound effects and music.
- [**image**](https://github.com/image-rs/image): Image loading and processing for textures and icons.

---

## Getting Started

Mirador is intended for developers and enthusiasts interested in graphics programming, game development, or Rust-based application architecture. To explore or contribute:

1. Ensure you have a recent Rust toolchain installed.
2. Clone the repository and build with `cargo build`.
3. Run the application with `cargo run`.

The game features a stealth-based gameplay loop where players navigate procedurally generated mazes while avoiding detection by AI enemies. Players can collect upgrades to enhance their abilities and progress through increasingly challenging levels.

For the in code documentation, please refer to:
- [**Rust Doc Documentation**](https://DetectiveFierce.github.io/mirador/mirador/index.html)

---

## License

Mirador is released under an open-source license. See the repository for details.
