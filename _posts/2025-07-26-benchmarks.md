---
layout: post
title: Benchmarking Library Overview
---

When developing a game like Mirador, it's important to understand where the program is spending its time. The benchmarking library provides a simple way to measure performance of different code sections and track frame rates. This isn't a sophisticated profiling system - it's just a collection of utilities to help identify slow parts of the code.

## What It Does

The benchmarking library consists of a few basic components:

- **Timers**: Measure how long code sections take to execute
- **Frame Rate Counter**: Track frame times and calculate FPS
- **Data Storage**: Keep track of measurements in memory
- **Output Functions**: Print results to console or save to files

The system is designed to be lightweight and have minimal impact on performance when not actively measuring.

## Core Components

### Timer Types

There are two main timer types for measuring code execution:

**Manual Timer**: You start it explicitly and stop it when done:

```rust
let timer = Timer::new("my_operation", config);
// ... do some work ...
let duration = timer.stop();
```

**Scoped Timer**: Automatically measures the time between when it's created and when it goes out of scope:

```rust
{
    let _timer = ScopedTimer::new("my_operation", config);
    // ... do some work ...
} // Timer automatically stops and records timing here
```

The scoped timer is convenient because you don't have to remember to stop it - it automatically records the timing when the variable goes out of scope.

### Frame Rate Counter

The `FrameRateCounter` tracks how long each frame takes to render:

```rust
pub struct FrameRateCounter {
    pub frame_times: Vec<Duration>,
    max_samples: usize,
    last_frame_time: Option<Instant>,
}
```

It keeps a rolling window of frame times and calculates the current FPS. This helps identify if the game is running smoothly or if there are performance issues.

### Data Storage

All measurements are stored in a central `BenchmarkData` structure:

```rust
pub struct BenchmarkData {
    measurements: HashMap<String, PerformanceMetrics>,
    config: BenchmarkConfig,
    fps_counter: FrameRateCounter,
}
```

Each measurement includes basic statistics like count, total time, minimum/maximum times, and average duration.

## Configuration

The `BenchmarkConfig` controls how the benchmarking system behaves:

```rust
pub struct BenchmarkConfig {
    pub enabled: bool,
    pub print_results: bool,
    pub write_to_file: bool,
    pub min_duration_threshold: Duration,
    pub max_samples: usize,
}
```

By default, benchmarking is only enabled in debug builds. This prevents the overhead from affecting release performance. You can also set minimum duration thresholds to filter out very fast operations that aren't worth measuring.

## Usage Examples

### Measuring a Function

```rust
use crate::benchmarks::utils::time;

let result = time("expensive_calculation", || {
    // ... do expensive work ...
    return some_value;
});
```

### Manual Timing

```rust
use crate::benchmarks::utils::scoped_timer;

{
    let _timer = scoped_timer("maze_generation");
    generate_maze();
} // Timing automatically recorded
```

### Printing Results

```rust
use crate::benchmarks::utils::print_summary;

// After running some benchmarks
print_summary();
```

This prints a formatted table showing all measurements, separated into initialization benchmarks and update benchmarks based on naming patterns.

## Output Format

The library provides several ways to view results:

- **Console Output**: Real-time printing as measurements are taken
- **Summary Tables**: Formatted tables showing all measurements
- **File Output**: Save results to timestamped files for later analysis

The summary output separates measurements into categories and shows statistics like total time, average time, and execution count for each measured operation.

## Limitations

This is a simple benchmarking system with some obvious limitations:

- It only measures wall-clock time, not CPU usage or memory
- No sampling or statistical analysis beyond basic min/max/avg
- Thread-safe but not optimized for high-frequency measurements
- File output is basic text format, not structured data

The system is designed for development-time performance analysis, not production monitoring.

## Integration

The benchmarking library is used throughout Mirador's codebase to measure performance of key operations like:

- Maze generation algorithms
- Rendering pipeline stages
- Audio processing
- Game state updates

It's particularly useful for identifying which parts of the code are taking the most time during development, helping focus optimization efforts on the right areas.

The library is intentionally simple - it's just a collection of timing utilities that make it easy to measure performance without adding much complexity to the codebase.
