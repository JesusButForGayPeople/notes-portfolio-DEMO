---
layout: post
title: The Herculean Task of Creating a Windows Binary 
---

Although I develop Mirador on Arch Linux (btw), I have always intended for the game to be accessible to a wider audience—including my friends, who actually get laid and use Windows as their primary operating system. Ensuring that Mirador runs smoothly on Windows was therefore not just a technical goal, but a practical necessity if I wanted others to play and enjoy the game.

Creating a Windows binary for Mirador turned out to be a much more complex journey than anticipated. I know that cross-platform development is never particularly easy. However, I figured that the platform-agnostic nature of all of Mirador's code would make the build process go relatively smoothly; *I was wrong*. What started as a simple request to compile the game for Windows users evolved into a months-long exploration of cross-platform development challenges, platform-specific input handling, and the intricacies of embedded assets. This post chronicles the entire journey and the technical solutions that emerged.

## The Initial Challenge

The journey began with a seemingly straightforward request: "help me build this project" on Windows. At first, I was briefly optimistic that I could simply cross-compile a Windows binary from my Linux machine. However, I quickly discovered that the Rust toolchain for Linux is not compatible with the Windows target in this context; the toolchains cause a dependency conflict with one another. As a result, it became clear that I had no choice but to actually boot into a Windows machine, set up a dedicated development environment, and proceed from there.

With the Windows toolchain set up, producing a Windows binary was straightforward from a technical standpoint. However, the resulting executable was not functional: none of the game’s assets were present. The binary launched, but all images, fonts, and audio were missing, leaving the application unable to render its interface or play sounds. This revealed a fundamental problem—while the build process itself was simple, asset management posed a significant obstacle: if I want a self contained executable I have to bake all of the assets into it, otherwise the program will look for the assets in the location that they are in within the project directory.

## Asset Embedding Revolution

The first major technical challenge was embedding all game assets into the binary. The original implementation loaded assets from the filesystem using relative paths, which works well on Linux but can be problematic on Windows due to different path handling and distribution requirements.

### The `include_bytes!()` Solution

I implemented a comprehensive asset embedding system using Rust's `include_bytes!()` macro. This approach embeds all assets directly into the binary at compile time, ensuring that the game can run without external asset files.

```rust
// Font assets
pub const HANKEN_GROTESK_REGULAR: &[u8] = include_bytes!("../fonts/HankenGrotesk/HankenGrotesk-Regular.ttf");
pub const HANKEN_GROTESK_MEDIUM: &[u8] = include_bytes!("../fonts/HankenGrotesk/HankenGrotesk-Medium.ttf");

// Image assets
pub const TITLE_IMAGE: &[u8] = include_bytes!("../assets/Mirador-title.png");
pub const SLIME_IMAGE: &[u8] = include_bytes!("../assets/Slime.png");

// Audio assets
pub const AUDIO_SINGLE_STEP: &[u8] = include_bytes!("../assets/audio/single_step.wav");
pub const AUDIO_UPGRADE: &[u8] = include_bytes!("../assets/audio/upgrade.ogg");
```

This change required updating every asset loading system in the codebase:
- **Audio system**: Switched from file-based loading to `StaticSoundData::from_cursor()`
- **Image renderers**: Updated to use `image::load_from_memory()` instead of `image::open()`
- **Font system**: Added `load_font_from_bytes()` method for embedded fonts
- **Icon system**: Created `load_texture_from_data()` for embedded textures

### Font Name Consistency Crisis

A critical issue emerged during the asset embedding process - font name inconsistencies were causing text to render as Wingdings characters. The problem was subtle but devastating:

```rust
// In assets.rs - fonts registered as:
"Hanken Grotesk" (with space)

// Throughout codebase - fonts referenced as:
"HankenGrotesk" (without space)
```

This mismatch meant that when the code requested "HankenGrotesk", the font system couldn't find it and fell back to system fonts, resulting in Wingdings display. The fix required an embarassingly long time to realize followed by hastily updating every font reference across the entire codebase to use the correct name with a space.

## Windows-Specific Input Handling

The most challenging aspect of the Windows port was the upgrade menu freezing issue. The game worked perfectly on Linux, but on Windows, selecting an upgrade would cause the screen to freeze while audio continued and debug output indicated the game process was still running.

### Root Cause Analysis

The issue stemmed from fundamental differences in how Windows and Linux handle mouse input events:

**Linux (X11/Wayland)**: Events are processed asynchronously with more lenient timing
**Windows (Win32)**: Has stricter event processing requirements and different mouse capture behavior

The problem was in the button click detection logic. On Windows, the mouse button release event might arrive **before** the button state has been properly updated to `Pressed`. This creates a timing issue where:

1. Mouse button is pressed → `mouse_pressed = true`
2. `update_button_states()` is called → button state becomes `Pressed`
3. Mouse button is released → `mouse_pressed = false`
4. **But on Windows, the release event might arrive before step 2 completes**

This means the button state might still be `Hover` when the release event is processed, causing the click to be missed entirely. The game would then fail to detect the button click, leaving the upgrade menu in an inconsistent state where it appeared to be processing the click (sound played, button pressed) but never actually registered the selection.

### The Fundamental Cause: Event Processing Timing

The core issue was a **race condition** in the event processing pipeline. Windows processes mouse events with stricter timing requirements than Linux, and the original button click detection logic assumed that button states would always be updated before the release event was processed.

The original logic was:
```rust
WindowEvent::MouseInput {
    state: ElementState::Released,
    button: MouseButton::Left,
    ..
} => {
    // Check for button clicks using current state
    for button in self.buttons.values() {
        if button.visible && button.enabled && button.state == ButtonState::Pressed {
            clicked_button = Some(button.id.clone());
            break;
        }
    }
    // ... rest of logic
}
```

This approach worked on Linux because the event processing was more forgiving, but failed on Windows where the release event could arrive before the button state update completed.

### The Solution: Multi-Layered Fallback Strategy

The solution required implementing a **multi-layered fallback strategy** that could handle the timing differences between platforms. The key insight was that we needed to force button state updates before checking for clicks, and provide multiple detection methods:

```rust
pub fn handle_input(&mut self, event: &WindowEvent) {
    match event {
        WindowEvent::MouseInput {
            state: ElementState::Released,
            button: MouseButton::Left,
            ..
        } => {
            // CRITICAL FIX: Force update button states before checking for clicks
            // This ensures button states are current on Windows
            self.update_button_states();
            
            // Multi-layered fallback strategy for cross-platform compatibility
            let mut clicked_button = None;
            
            // Layer 1: Check current button states (works on Linux)
            for button in self.buttons.values() {
                if button.visible && button.enabled && button.state == ButtonState::Pressed {
                    clicked_button = Some(button.id.clone());
                    break;
                }
            }
            
            // Layer 2: Check pressed_buttons set for timing issues (Windows fallback)
            if clicked_button.is_none() {
                for button_id in &self.pressed_buttons {
                    if let Some(button) = self.buttons.get(button_id) {
                        if button.visible && button.enabled && 
                           button.contains_point(self.mouse_position.0, self.mouse_position.1) {
                            clicked_button = Some(button_id.clone());
                            break;
                        }
                    }
                }
            }
            
            // Layer 3: Check hover state as final fallback
            if clicked_button.is_none() {
                for button in self.buttons.values() {
                    if button.visible && button.enabled && 
                       button.contains_point(self.mouse_position.0, self.mouse_position.1) {
                        clicked_button = Some(button.id.clone());
                        break;
                    }
                }
            }
            
            if let Some(clicked_id) = clicked_button {
                self.just_clicked = Some(clicked_id);
            }
            
            self.mouse_pressed = false;
            self.pressed_buttons.clear();
            self.update_button_states();
        }
        // ... other event handling
    }
}
```

The critical fix was **forcing button state updates before checking for clicks**. This ensures that on Windows, where event timing is stricter, the button states are properly updated before we attempt to detect clicks. The multi-layered approach provides three different detection methods:

1. **Primary**: Check current button states (works reliably on Linux)
2. **Secondary**: Check the pressed_buttons tracking set (handles Windows timing issues)
3. **Tertiary**: Check hover state as a final fallback (catches edge cases)

This approach ensures that clicks are detected reliably across both platforms, regardless of the underlying event processing differences.

### Rendering Pipeline Fix

A secondary but equally critical issue was discovered in the rendering logic. The upgrade menu was being rendered based on screen state alone, without checking if the menu was actually visible:

```rust
// Before (problematic):
if state.game_state.current_screen == CurrentScreen::UpgradeMenu {

// After (fixed):
if state.game_state.current_screen == CurrentScreen::UpgradeMenu && 
   state.upgrade_menu.is_visible() {
```

This fix was essential because when an upgrade was selected, the upgrade menu would call `hide()` to set `visible = false`, but the screen state remained `CurrentScreen::UpgradeMenu`. This created a situation where:

1. The upgrade menu was hidden (`visible = false`)
2. The screen state was still `UpgradeMenu`
3. The rendering code continued trying to render the menu
4. This caused a **rendering conflict** that froze the display

The fix ensured that the rendering code only attempts to render the upgrade menu when both conditions are met: the screen is in upgrade menu mode AND the menu is actually visible. This prevents the rendering conflict that was causing the display freeze.

## High DPI and Text Scaling

Another challenge was ensuring proper text scaling for high DPI displays on Windows. The upgrade menu text needed to scale appropriately based on window size, similar to how the pause menu handled it.

### Virtual DPI Scaling Implementation

I implemented a virtual DPI scaling system that ensures consistent text sizing across different screen resolutions by adapting the system we use to position the pause menu text:

```rust
fn scaled_text_style(window_height: f32) -> crate::renderer::text::TextStyle {
    // Virtual DPI scaling based on reference height
    let reference_height = 1080.0;
    let scale = (window_height / reference_height).clamp(0.7, 2.0);
    let font_size = (32.0 * scale).clamp(16.0, 48.0);
    let line_height = (48.0 * scale).clamp(24.0, 72.0);

    crate::renderer::text::TextStyle {
        font_family: "Hanken Grotesk".to_string(),
        font_size,
        line_height,
        color: Color::rgb(50, 50, 50),
        weight: glyphon::Weight::MEDIUM,
        style: glyphon::Style::Normal,
    }
}
```

This approach scales text proportionally with window size while maintaining reasonable bounds, ensuring readability across different display configurations.

## Window Management and Maximization

When I first double-clicked the `.exe` file on Windows, the game launched with two separate windows: a terminal window for console output, and a second, extremely small window for the game itself. This made the game nearly unplayable—the main window was so tiny that the interface was unusable. Complicating matters, the game’s mouse locking behavior (which captures the cursor for gameplay) made it difficult to manually resize the window after launch.

To address this, I needed to ensure that the game window would open maximized by default on Windows. This required explicit handling during window creation so that users would immediately see the game at a usable size, without needing to fight the mouse capture or manually adjust the window.

```rust
fn resumed(&mut self, event_loop: &ActiveEventLoop) {
    // Create window with maximized state
    let window_attributes = Window::default_attributes()
        .with_maximized(true);
        
    let window = match event_loop.create_window(window_attributes) {
        Ok(window) => window,
        Err(err) => {
            panic!("Failed to create window: {}", err);
        }
    };
    
    pollster::block_on(self.set_window(window));
}
```

This ensures the window opens maximized on Windows while maintaining compatibility with other platforms.


## Performance and Memory Considerations

Embedding all assets in the binary had only a modest impact on the executable size—the final `.exe` is about 20 MiB (with the linux binary being 25.2 MiB). This increase in binary size was well worth it since  provides the following benefits:

- **Self-contained distribution**: No external asset files required
- **Faster loading**: Assets loaded from memory instead of disk
- **Cross-platform compatibility**: No path issues on different operating systems
- **Reliable deployment**: Eliminates missing asset file scenarios

The trade-off was acceptable given the improved user experience and distribution reliability.

## Debugging and Development Tools

Throughout the process, comprehensive debugging tools were essential for diagnosing cross-platform issues:

- **Debug logging**: Added extensive logging to track mouse events and button states
- **Platform-specific conditionals**: Used `#[cfg(target_os = "windows")]` for platform-specific code
- **Event loop configuration**: Adjusted control flow for different platforms
- **Asset verification**: Implemented checks to ensure all embedded assets load correctly

## Lessons Learned

This journey revealed several important lessons about cross-platform development:

### 1. Platform Differences Are Subtle but Critical
The mouse input timing differences between Windows and Linux were not obvious but caused significant issues. Understanding platform-specific behavior is essential.

### 2. Asset Management Requires Careful Planning
Embedding assets provides many benefits but requires systematic updates across the entire codebase. Font name consistency is particularly critical.

### 3. Event Handling Needs Platform Awareness
Input event processing can vary significantly between platforms. Robust fallback strategies are essential for reliable cross-platform behavior.

### 4. Rendering Pipeline Must Consider State Management
The relationship between game state and rendering state must be carefully managed, especially during transitions.

### 5. Debugging Tools Are Essential
Comprehensive logging and platform-specific debugging tools are invaluable for diagnosing cross-platform issues.

## The Final Result

After a little bit more than a month of development and countless iterations, Mirador now runs reliably on both Linux AND Windows with:

- ✅ **Self-contained binary** with all assets embedded
- ✅ **Proper font rendering** without Wingdings characters
- ✅ **Reliable upgrade menu** that works consistently on Windows
- ✅ **High DPI support** with proper text scaling
- ✅ **Maximized window** behavior on Windows
- ✅ **Cross-platform compatibility** maintained with Linux

The journey from a Linux-only game to a (hopefully) robust cross-platform Windows binary involved solving numerous technical challenges, but the result is a much more user-friendly application. The lessons learned about cross-platform development will continue to inform the future of the project and help avoid similar issues in the future. Although, I am afraid that cross platform compatability issues will continue to haunt me as I continue to expand the engine.

The experience demonstrates that cross-platform development requires not just technical skill, but also patience, systematic debugging, a deep understanding of platform-specific behaviors, and certainly a degree of self hatred. What started as a simple compilation request evolved into a comprehensive exploration of just how much I do not like Windows.