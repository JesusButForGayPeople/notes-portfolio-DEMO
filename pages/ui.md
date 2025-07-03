---
layout: page
title: User Interface (egui)
permalink: /ui/
---

Modern game development and graphics applications require sophisticated user interfaces that can coexist seamlessly with high-performance GPU rendering. This article explores Mirador's egui integration with wgpu that demonstrates how to build debug interfaces, manage GPU resources efficiently, and create custom themes for immediate-mode GUI systems.

## Understanding the Integration Architecture

The integration between egui and wgpu represents a careful balance between immediate-mode GUI principles and retained-mode GPU rendering. The `EguiRenderer` struct serves as the central coordinator, managing the translation between egui's immediate-mode UI descriptions and wgpu's command-based rendering system.

The renderer maintains three critical components: a `State` that handles input processing and UI context management, a `Renderer` that manages GPU resources and tessellation, and a frame lifecycle tracker that ensures proper synchronization between UI updates and GPU operations.

```rust
pub struct EguiRenderer {
    state: State,
    renderer: Renderer,
    frame_started: bool,
}
```

This architecture allows the system to process UI definitions on each frame while efficiently managing GPU resources that may persist across multiple frames.

## Frame Lifecycle Management

The frame lifecycle in this integration follows a strict pattern that ensures proper resource management and rendering order. Each frame begins with `begin_frame()`, which processes accumulated input events and prepares the egui context for UI construction.

```rust
pub fn begin_frame(&mut self, window: &Window) {
    let raw_input = self.state.take_egui_input(window);
    self.state.egui_ctx().begin_pass(raw_input);
    self.frame_started = true;
}
```

During the frame, application code can access the egui context to build UI elements. The context provides the complete egui API for creating windows, panels, controls, and handling user interactions.

The frame concludes with `end_frame_and_draw()`, which performs the complex task of converting egui's UI description into GPU-renderable geometry, updating GPU resources, and recording render commands.

## GPU Resource Management Strategy

The integration employs a sophisticated resource management strategy that balances performance with memory efficiency. The renderer maintains a texture atlas for UI elements, vertex and index buffers for geometry, and shader resources for rendering.

```rust
pub fn end_frame_and_draw(
    &mut self,
    device: &Device,
    queue: &Queue,
    encoder: &mut CommandEncoder,
    window: &Window,
    window_surface_view: &TextureView,
    screen_descriptor: ScreenDescriptor,
) {
    let full_output = self.state.egui_ctx().end_pass();

    let tris = self
        .state
        .egui_ctx()
        .tessellate(full_output.shapes, self.state.egui_ctx().pixels_per_point());

    for (id, image_delta) in &full_output.textures_delta.set {
        self.renderer
            .update_texture(device, queue, *id, image_delta);
    }
}
```

The tessellation process converts egui's high-level UI descriptions into triangulated geometry suitable for GPU rendering. This happens on each frame, allowing for completely dynamic UI layouts while maintaining efficient GPU resource utilization.

## Texture Management and Updates

The system handles texture updates incrementally, processing only changed portions of the UI texture atlas. This approach minimizes GPU memory bandwidth usage while supporting dynamic UI elements like animated icons or real-time data displays.

The texture delta system tracks additions and removals, ensuring that GPU memory is properly managed even in applications with frequently changing UI content.

```rust
for x in &full_output.textures_delta.free {
    self.renderer.free_texture(x)
}
```

This cleanup phase ensures that unused textures are immediately freed, preventing memory leaks in long-running applications.

## Custom Theme Implementation

The theme system demonstrates how to create cohesive visual designs that integrate well with game environments. The `ui_theme()` function returns a complete visual configuration that defines every aspect of the UI appearance.

```rust
pub fn ui_theme() -> Result<Visuals, String> {
    macro_rules! color {
        ($hex:expr) => {
            Color32::from_hex($hex).map_err(|e| format!("Invalid color {}: {:?}", $hex, e))?
        };
    }
}
```

The theme system includes comprehensive error handling that gracefully falls back to default themes when custom theme loading fails. This approach ensures that UI systems remain functional even when theme resources are missing or corrupted.

```rust
match egui_lib::ui_theme() {
    Ok(visuals) => ui.ctx().set_visuals(visuals),
    Err(e) => {
        eprintln!("Failed to load custom theme: {}", e);
        ui.ctx().set_visuals(egui::Visuals::dark());
    }
}
```


## Practical UI Implementation

The `UiState` struct demonstrates how to organize UI state in a game application. It maintains both immediate UI concerns like slider values and longer-term state like elapsed time and color values.

```rust
pub struct UiState {
    pub show_sliders: bool,
    pub r: f32,
    pub g: f32,
    pub b: f32,
    pub start_time: std::time::Instant,
    pub elapsed_time: f32,
    pub slider_1: f32,
    pub slider_2: f32,
}
```

This separation allows the UI system to persist important state across frames while remaining responsive to user interactions.

## Building Debug Interfaces

The debug interface implementation shows how to create comprehensive debugging tools that integrate seamlessly with the main application. The `update_ui` method constructs a complete debug panel with real-time information display and interactive controls.

```rust
ui.label(format!(
    "Position:  x: {:.2},  y: {:.2},  z: {:.2}",
    pos[0], pos[1], pos[2]
));
ui.label(format!(
    "Pitch: {:.2}   Yaw: {:.2}   Speed: {:.2}",
    self.game_state.player.pitch,
    self.game_state.player.yaw,
    self.game_state.player.speed
));
```

The interface provides immediate feedback about game state, allowing developers to observe system behavior in real-time and make adjustments through interactive controls.

## Custom Widget Development

The `custom_slider` function is very similar to the built-in `Slider` widget, but it allows the text label to appear before the slider rather than after it.

```rust
fn custom_slider(
    ui: &mut egui::Ui,
    label: &str,
    value: &mut f32,
    range: std::ops::RangeInclusive<f32>,
    speed: f64,
    decimals: usize,
) {
    ui.horizontal(|ui| {
        ui.label(label);
        ui.add(
            egui::DragValue::new(value)
                .speed(speed)
                .fixed_decimals(decimals)
                .range(range.clone())
                .suffix(""),
        );
        ui.add(egui::Slider::new(value, range).show_value(false));
    });
}
```


## Integration with Game Systems

The integration pattern shown in the code demonstrates how UI systems can access and modify game state safely. The UI system receives mutable references to game state components, allowing for real-time debugging and parameter adjustment.

The conditional UI display mechanism allows developers to toggle debug interfaces on and off, ensuring that performance-critical builds can omit UI overhead when not needed.

## Performance Considerations

The integration carefully manages performance by minimizing GPU state changes and batching UI rendering operations. The render pass setup reuses existing framebuffer contents, allowing UI elements to overlay game content without requiring full-screen clearing operations.

The immediate-mode approach ensures that UI performance scales with visible complexity rather than total UI definition complexity, making it suitable for applications with large amounts of conditional UI content.
