---
layout: page
title: User Interface System
permalink: /ui/
---

Modern game development requires sophisticated user interfaces that can coexist seamlessly with high-performance GPU rendering. This article explores Mirador's custom UI system built with wgpu that demonstrates how to build responsive interfaces, manage GPU resources efficiently, and create custom themes for game-specific user interfaces.

## Understanding the UI Architecture

The custom UI system represents a careful balance between game-specific interface requirements and high-performance GPU rendering. The `ButtonManager` struct serves as the central coordinator, managing the translation between high-level UI descriptions and wgpu's command-based rendering system.

The system maintains several critical components: a `TextRenderer` for text display, a `RectangleRenderer` for button backgrounds, an `IconRenderer` for visual elements, and input handling that ensures proper synchronization between UI updates and GPU operations.

```rust
pub struct ButtonManager {
    pub buttons: HashMap<String, Button>,
    pub button_order: Vec<String>,
    pub text_renderer: TextRenderer,
    pub rectangle_renderer: RectangleRenderer,
    pub icon_renderer: IconRenderer,
    pub window_size: PhysicalSize<u32>,
    pub mouse_position: (f32, f32),
    pub mouse_pressed: bool,
    pub just_clicked: Option<String>,
    pub container_rect: Option<Rectangle>,
    pub last_mouse_position: (f32, f32),
    pub last_mouse_pressed: bool,
}
```

This architecture allows the system to process UI definitions efficiently while managing GPU resources that persist across multiple frames.

## Frame Lifecycle Management

The frame lifecycle in this system follows a strict pattern that ensures proper resource management and rendering order. Each frame begins with input processing, which updates mouse position and button states based on window events.

```rust
pub fn handle_input(&mut self, event: &WindowEvent) {
    match event {
        WindowEvent::CursorMoved { position, .. } => {
            self.mouse_position = (position.x as f32, position.y as f32);
            self.update_button_states();
        }
        WindowEvent::MouseInput { state, .. } => {
            self.mouse_pressed = *state == ElementState::Pressed;
            self.update_button_states();
        }
        // ... other event handling
    }
}
```

During the frame, the system processes button interactions and updates visual states. The rendering phase draws all UI elements in the correct order: backgrounds, icons, and text.

The frame concludes with the render pass, which efficiently batches all UI elements and submits them to the GPU in a single operation.

## GPU Resource Management Strategy

The system employs a sophisticated resource management strategy that balances performance with memory efficiency. The renderer maintains separate pipelines for text, rectangles, and icons, each optimized for their specific content type.

```rust
pub fn render(
    &mut self,
    device: &Device,
    render_pass: &mut RenderPass,
) -> Result<(), glyphon::RenderError> {
    self.rectangle_renderer.clear_rectangles();
    
    // Add button backgrounds
    for button_id in &self.button_order {
        if let Some(button) = self.buttons.get(button_id) {
            if button.visible {
                let (actual_x, actual_y) = button.position.calculate_actual_position();
                let color = match button.state {
                    ButtonState::Normal => button.style.background_color,
                    ButtonState::Hover => button.style.hover_color,
                    ButtonState::Pressed => button.style.pressed_color,
                    ButtonState::Disabled => button.style.disabled_color,
                };

                let rectangle = Rectangle::new(actual_x, actual_y, button.position.width, button.position.height, color)
                    .with_corner_radius(button.style.corner_radius);

                self.rectangle_renderer.add_rectangle(rectangle);
            }
        }
    }

    self.rectangle_renderer.render(device, render_pass);
    self.icon_renderer.render(device, render_pass);
    self.text_renderer.render(render_pass)
}
```

The rendering process efficiently batches UI elements by type, allowing for optimal GPU utilization while maintaining clean separation between different visual components.

## Texture Management and Updates

The system handles texture updates efficiently, processing only the specific UI elements that need to be rendered. This approach minimizes GPU memory bandwidth usage while supporting dynamic UI elements like animated icons or real-time data displays.

The icon renderer manages texture resources for UI icons, ensuring that GPU memory is properly managed even in applications with frequently changing UI content.

```rust
pub fn update_icon_positions(&mut self) {
    self.icon_renderer.clear_icons();

    for button_id in &self.button_order {
        if let Some(button) = self.buttons.get(button_id) {
            if button.visible && button.icon_id.is_some() {
                let (actual_x, actual_y) = button.position.calculate_actual_position();
                let icon = Icon::new(
                    actual_x + button.position.width * 0.1,
                    actual_y + button.position.height * 0.1,
                    button.position.width * 0.8,
                    button.position.height * 0.8,
                    button.icon_id.clone().unwrap(),
                );
                self.icon_renderer.add_icon(icon);
            }
        }
    }
}
```

This approach ensures that only visible icons are rendered, preventing unnecessary GPU operations and memory usage.

## Custom Theme Implementation

The theme system demonstrates how to create cohesive visual designs that integrate well with game environments. The button styling system provides functions that return complete visual configurations for different button types.

```rust
pub fn create_primary_button_style() -> ButtonStyle {
    ButtonStyle {
        background_color: Color::rgb(52, 152, 219),
        hover_color: Color::rgb(41, 128, 185),
        pressed_color: Color::rgb(36, 113, 163),
        disabled_color: Color::rgb(149, 165, 166),
        corner_radius: 8.0,
        text_style: TextStyle {
            font_family: "HankenGrotesk".to_string(),
            font_size: 18.0,
            line_height: 20.0,
            color: Color::rgb(255, 255, 255),
            weight: Weight::MEDIUM,
            style: Style::Normal,
        },
        spacing: ButtonSpacing::Wrap,
    }
}
```

The theme system includes comprehensive styling options that ensure consistent visual appearance across all UI elements. This approach creates a cohesive user experience that matches the game's visual identity.


## Practical UI Implementation

The `ButtonManager` struct demonstrates how to organize UI state in a game application. It maintains both immediate UI concerns like button states and longer-term state like window size and mouse position.

```rust
pub struct ButtonManager {
    pub buttons: HashMap<String, Button>,
    pub button_order: Vec<String>,
    pub text_renderer: TextRenderer,
    pub rectangle_renderer: RectangleRenderer,
    pub icon_renderer: IconRenderer,
    pub window_size: PhysicalSize<u32>,
    pub mouse_position: (f32, f32),
    pub mouse_pressed: bool,
    pub just_clicked: Option<String>,
    pub container_rect: Option<Rectangle>,
    pub last_mouse_position: (f32, f32),
    pub last_mouse_pressed: bool,
}
```

This separation allows the UI system to persist important state across frames while remaining responsive to user interactions.

## Building Game Interfaces

The pause menu implementation shows how to create comprehensive game interfaces that integrate seamlessly with the main application. The menu system constructs complete UI panels with real-time information display and interactive controls.

```rust
pub fn create_menu_buttons(button_manager: &mut ButtonManager, window_size: PhysicalSize<u32>) {
    let reference_height = 1080.0;
    let scale = (window_size.height as f32 / reference_height).clamp(0.7, 2.0);

    let button_width = (window_size.width as f32 * 0.38 * scale).clamp(180.0, 600.0);
    let button_height = (window_size.height as f32 * 0.09 * scale).clamp(32.0, 140.0);
    let button_spacing = (window_size.height as f32 * 0.015 * scale).clamp(2.0, 24.0);

    let total_height = button_height * 5.0 + button_spacing * 4.0;
    let center_x = window_size.width as f32 / 2.0;
    let start_y = (window_size.height as f32 - total_height) / 2.0;
}
```

The interface provides immediate feedback about game state, allowing players to interact with the game through intuitive controls that scale appropriately across different screen sizes.

## Custom Widget Development

The button system supports various spacing strategies that allow for flexible layout creation. The `ButtonSpacing` enum provides different approaches for button sizing and positioning.

```rust
#[derive(Debug, Clone, PartialEq)]
pub enum ButtonSpacing {
    Wrap,           // Button size matches text content
    Hbar(f32),      // Button width proportional to container width
    Tall(f32),      // Button height proportional to container height
}

impl ButtonSpacing {
    pub fn calculate_size(&self, text_width: f32, text_height: f32, container_size: (f32, f32)) -> (f32, f32) {
        match self {
            ButtonSpacing::Wrap => (text_width + 20.0, text_height + 10.0),
            ButtonSpacing::Hbar(proportion) => (container_size.0 * proportion, text_height + 10.0),
            ButtonSpacing::Tall(height_proportion) => (text_width + 20.0, container_size.1 * height_proportion),
        }
    }
}
```

This flexibility allows the system to create both compact layouts and structured grid interfaces as needed.


## Integration with Game Systems

The integration pattern shown in the code demonstrates how UI systems can access and modify game state safely. The UI system receives mutable references to game state components, allowing for real-time interaction and parameter adjustment.

The conditional UI display mechanism allows the game to show and hide interfaces as needed, ensuring that performance-critical gameplay can omit UI overhead when not required.

## Performance Considerations

The system carefully manages performance by minimizing GPU state changes and batching UI rendering operations. The render pass setup efficiently batches all UI elements by type, allowing UI elements to overlay game content without requiring full-screen clearing operations.

The component-based approach ensures that UI performance scales with visible complexity rather than total UI definition complexity, making it suitable for applications with large amounts of conditional UI content.
