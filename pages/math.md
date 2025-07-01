---
layout: page
title: Math Utilities
permalink: /math/
---

# Math Utilities

This module provides essential mathematical types and operations for 3D graphics transformations, specifically designed for use with WGPU and WGSL shaders.

## 4x4 Matrix (Mat4)

A memory-compatible 4x4 matrix type with common transformation constructors and operations.

### Implementation Details

- **Storage**: Matrices are stored in column-major order for compatibility with WGSL/GPU
- **Coordinate System**: Right-handed coordinate system by default
- **Depth Range**: Perspective matrices use OpenGL-style depth range (-1 to 1)
- **Angles**: Rotation angles are specified in degrees for convenience
- **Inverse**: The `inverse()` method includes a fallback to identity for singular matrices

### Performance Notes

- Matrix multiplication uses a naive implementation
- For production use, consider optimizing with SIMD or a dedicated math library
- Inverse calculation is optimized specifically for affine transformations

### Coordinate System

- **X-axis**: Right
- **Y-axis**: Up  
- **Z-axis**: Back (negative Z is forward)
- **Rotation**: Follows right-hand rule

## 3D Vector (Vec3)

A memory-compatible 3D vector type with common vector operations.

### Implementation Details

- **Storage**: Vectors stored as `[f32; 3]` with no padding (12 bytes total)
- **Compatibility**: All operations maintain WGPU memory compatibility
- **Coordinate System**: Right-handed coordinate system by default
- **Normalization**: Handles zero vectors gracefully
- **Optimization**: No SIMD optimizations in current implementation

### Performance Notes

- Basic operations use naive implementations
- Consider SIMD for performance-critical code
- Normalization includes a branch for zero vectors
- No explicit alignment directives (relies on f32's natural alignment)

### Coordinate System

- **X-axis**: Right
- **Y-axis**: Up
- **Z-axis**: Forward (right-handed system)
- **Cross Products**: Follow right-hand rule

## Usage

These math utilities are designed to work seamlessly with WGPU's graphics pipeline and WGSL shaders, providing the foundation for all 3D transformations and vector operations in the Mirador engine.
