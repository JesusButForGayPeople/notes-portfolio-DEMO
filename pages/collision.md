---
layout: subpage
title: Collision Detection via Bounding Volume Hierarchies
permalink: /collision/
---


This guide explains how the 3D collision detection system works, using a Bounding Volume Hierarchy (BVH) for efficient spatial partitioning and physics-based collision resolution.

## Overview

The collision system consists of several key components working together:

1. **AABB (Axis-Aligned Bounding Box)** - Simple collision primitives
2. **WallFace** - Individual wall surfaces with orientation
3. **BVH (Bounding Volume Hierarchy)** - Spatial acceleration structure
4. **CollisionSystem** - High-level collision management

## 1. Axis-Aligned Bounding Box (AABB)

The AABB is the fundamental collision primitive - a rectangular box aligned with world axes.

```rust
#[derive(Debug, Clone)]
pub struct AABB {
    pub min: [f32; 3],
    pub max: [f32; 3],
}

impl AABB {
    pub fn new(min: [f32; 3], max: [f32; 3]) -> Self {
        Self { min, max }
    }

    pub fn from_wall_face(p1: [f32; 3], p2: [f32; 3], p3: [f32; 3], p4: [f32; 3]) -> Self {
        let min_x = p1[0].min(p2[0]).min(p3[0]).min(p4[0]);
        let min_y = p1[1].min(p2[1]).min(p3[1]).min(p4[1]);
        let min_z = p1[2].min(p2[2]).min(p3[2]).min(p4[2]);

        let max_x = p1[0].max(p2[0]).max(p3[0]).max(p4[0]);
        let max_y = p1[1].max(p2[1]).max(p3[1]).max(p4[1]);
        let max_z = p1[2].max(p2[2]).max(p3[2]).max(p4[2]);

        Self::new([min_x, min_y, min_z], [max_x, max_y, max_z])
    }

    pub fn intersects(&self, other: &AABB) -> bool {
        for i in 0..3 {
            if self.max[i] < other.min[i] || self.min[i] > other.max[i] {
                return false;
            }
        }
        true
    }

    pub fn center(&self) -> [f32; 3] {
        [
            (self.min[0] + self.max[0]) * 0.5,
            (self.min[1] + self.max[1]) * 0.5,
            (self.min[2] + self.max[2]) * 0.5,
        ]
    }
}
```

**Key Functions:**
- `intersects()` - Fast AABB-AABB collision test using separating axis theorem
- `from_wall_face()` - Creates bounding box from four corner points
- `center()` - Used for spatial sorting and distance calculations

## 2. Wall Face Representation

Wall faces are quadrilateral surfaces with orientation information.

```rust
#[derive(Debug, Clone)]
pub struct WallFace {
    pub corners: [[f32; 3]; 4],
    pub normal: [f32; 3],
    pub aabb: AABB,
}

impl WallFace {
    pub fn new(corners: [[f32; 3]; 4]) -> Self {
        let normal = Self::calculate_normal(&corners);
        let aabb = AABB::from_wall_face(corners[0], corners[1], corners[2], corners[3]);

        Self {
            corners,
            normal,
            aabb,
        }
    }

    fn calculate_normal(corners: &[[f32; 3]; 4]) -> [f32; 3] {
        let u = [
            corners[1][0] - corners[0][0],
            corners[1][1] - corners[0][1],
            corners[1][2] - corners[0][2],
        ];
        let v = [
            corners[2][0] - corners[0][0],
            corners[2][1] - corners[0][1],
            corners[2][2] - corners[0][2],
        ];

        let normal = [
            v[1] * u[2] - v[2] * u[1],
            v[2] * u[0] - v[0] * u[2],
            v[0] * u[1] - v[1] * u[0],
        ];

        let len = (normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2]).sqrt();
        [normal[0] / len, normal[1] / len, normal[2] / len]
    }
}
```

**Key Features:**
- Stores four corner points defining the wall surface
- Calculates normal vector using cross product for collision response
- Maintains AABB for fast intersection tests

## 3. Bounding Volume Hierarchy (BVH)

The BVH is a binary tree that spatially partitions wall faces for efficient collision queries.

```rust
#[derive(Debug, Clone)]
pub enum BVHNode {
    Leaf {
        aabb: AABB,
        faces: Vec<WallFace>,
    },
    Internal {
        aabb: AABB,
        left: Box<BVHNode>,
        right: Box<BVHNode>,
    },
}

#[derive(Debug, Default, Clone)]
pub struct BVH {
    pub root: Option<BVHNode>,
}

impl BVH {
    pub fn build(&mut self, faces: Vec<WallFace>) {
        if faces.is_empty() {
            self.root = None;
            return;
        }
        self.root = Some(Self::build_recursive(faces));
    }

    fn build_recursive(mut faces: Vec<WallFace>) -> BVHNode {
        if faces.len() <= 4 {
            let mut aabb = faces[0].aabb.clone();
            for face in faces.iter().skip(1) {
                aabb.expand(&face.aabb);
            }
            return BVHNode::Leaf { aabb, faces };
        }

        let (split_axis, _split_pos) = Self::find_best_split(&faces);

        faces.sort_by(|a, b| {
            let a_center = a.aabb.center()[split_axis];
            let b_center = b.aabb.center()[split_axis];
            a_center.partial_cmp(&b_center).unwrap()
        });

        let mid = faces.len() / 2;
        let left_faces = faces.drain(..mid).collect();
        let right_faces = faces;

        let left_child = Self::build_recursive(left_faces);
        let right_child = Self::build_recursive(right_faces);

        let mut aabb = left_child.aabb().clone();
        aabb.expand(right_child.aabb());

        BVHNode::Internal {
            aabb,
            left: Box::new(left_child),
            right: Box::new(right_child),
        }
    }
}
```

**BVH Construction Process:**
1. If few faces (≤4), create leaf node
2. Find best axis to split on
3. Sort faces along that axis
4. Split into two equal groups
5. Recursively build left and right subtrees
6. Create parent node with combined bounding box

## 4. Collision Query System

The BVH enables fast collision queries by pruning branches that can't contain collisions.

```rust
impl BVH {
    pub fn query_collisions(&self, player_aabb: &AABB) -> Vec<&WallFace> {
        let mut results = Vec::new();
        if let Some(ref root) = self.root {
            Self::query_recursive(root, player_aabb, &mut results);
        }
        results
    }

    fn query_recursive<'a>(node: &'a BVHNode, query_aabb: &AABB, results: &mut Vec<&'a WallFace>) {
        if !node.aabb().intersects(query_aabb) {
            return;
        }

        match node {
            BVHNode::Leaf { faces, .. } => {
                for face in faces {
                    if face.aabb.intersects(query_aabb) {
                        results.push(face);
                    }
                }
            }
            BVHNode::Internal { left, right, .. } => {
                Self::query_recursive(left, query_aabb, results);
                Self::query_recursive(right, query_aabb, results);
            }
        }
    }
}
```

**Query Algorithm:**
1. Start at root node
2. If node's AABB doesn't intersect query, skip entire subtree
3. If leaf node, test each face individually
4. If internal node, recursively check both children

## 5. Collision System Integration

The high-level collision system manages the entire process.

```rust
#[derive(Debug, Default, Clone)]
pub struct CollisionSystem {
    pub bvh: BVH,
    pub player_radius: f32,
    pub player_height: f32,
}

impl CollisionSystem {
    pub fn new(player_radius: f32, player_height: f32) -> Self {
        Self {
            bvh: BVH::new(),
            player_radius,
            player_height,
        }
    }

    pub fn build_from_maze(&mut self, maze_grid: &[Vec<bool>]) {
        let wall_faces = self.extract_wall_faces_from_maze(maze_grid);
        self.bvh.build(wall_faces);
    }

    pub fn check_and_resolve_collision(
        &self,
        current_pos: [f32; 3],
        desired_pos: [f32; 3],
    ) -> [f32; 3] {
        let player_aabb = AABB::new(
            [
                desired_pos[0] - self.player_radius,
                desired_pos[1],
                desired_pos[2] - self.player_radius,
            ],
            [
                desired_pos[0] + self.player_radius,
                desired_pos[1] + self.player_height,
                desired_pos[2] + self.player_radius,
            ],
        );

        let potential_collisions = self.bvh.query_collisions(&player_aabb);

        if potential_collisions.is_empty() {
            return desired_pos;
        }

        let mut resolved_pos = desired_pos;
        let max_iterations = 5;

        for _ in 0..max_iterations {
            let player_aabb = AABB::new(
                [
                    resolved_pos[0] - self.player_radius,
                    resolved_pos[1],
                    resolved_pos[2] - self.player_radius,
                ],
                [
                    resolved_pos[0] + self.player_radius,
                    resolved_pos[1] + self.player_height,
                    resolved_pos[2] + self.player_radius,
                ],
            );

            let potential_collisions = self.bvh.query_collisions(&player_aabb);
            if potential_collisions.is_empty() {
                break;
            }

            let mut closest_face = &potential_collisions[0];
            let mut closest_distance = f32::MAX;

            for face in &potential_collisions {
                let face_center = face.aabb.center();
                let distance = ((face_center[0] - resolved_pos[0]).powi(2)
                    + (face_center[1] - resolved_pos[1]).powi(2)
                    + (face_center[2] - resolved_pos[2]).powi(2))
                .sqrt();

                if distance < closest_distance {
                    closest_distance = distance;
                    closest_face = face;
                }
            }

            let movement = [
                resolved_pos[0] - current_pos[0],
                resolved_pos[1] - current_pos[1],
                resolved_pos[2] - current_pos[2],
            ];

            resolved_pos =
                self.resolve_wall_collision(current_pos, resolved_pos, movement, closest_face);

            let epsilon = 0.0001;
            let position_changed = (resolved_pos[0] - current_pos[0]).abs() > epsilon
                || (resolved_pos[1] - current_pos[1]).abs() > epsilon
                || (resolved_pos[2] - current_pos[2]).abs() > epsilon;

            if !position_changed {
                break;
            }
        }

        resolved_pos
    }
}
```

## 6. Wall Sliding Physics

The collision resolution uses vector projection to enable realistic wall sliding.

```rust
impl CollisionSystem {
    fn resolve_wall_collision(
        &self,
        current_pos: [f32; 3],
        desired_pos: [f32; 3],
        movement: [f32; 3],
        wall_face: &WallFace,
    ) -> [f32; 3] {
        let normal = wall_face.normal;

        let movement_dir = [
            desired_pos[0] - current_pos[0],
            desired_pos[1] - current_pos[1],
            desired_pos[2] - current_pos[2],
        ];

        let approach_dot =
            movement_dir[0] * normal[0] + movement_dir[1] * normal[1] + movement_dir[2] * normal[2];

        let effective_normal = if approach_dot < 0.0 {
            normal
        } else {
            [-normal[0], -normal[1], -normal[2]]
        };

        let movement_dot = movement[0] * effective_normal[0]
            + movement[1] * effective_normal[1]
            + movement[2] * effective_normal[2];

        if movement_dot < 0.0 {
            let slide_movement = [
                movement[0] - movement_dot * effective_normal[0],
                movement[1] - movement_dot * effective_normal[1],
                movement[2] - movement_dot * effective_normal[2],
            ];

            return [
                current_pos[0] + slide_movement[0],
                current_pos[1] + slide_movement[1],
                current_pos[2] + slide_movement[2],
            ];
        }

        desired_pos
    }
}
```

**Wall Sliding Algorithm:**
1. Calculate movement direction and wall normal
2. Determine effective normal (opposing player movement)
3. Calculate component of movement into the wall
4. Remove that component, leaving only parallel movement
5. Apply the "slide" movement to the current position

## 7. Player Movement Integration

The player movement system integrates with collision detection.

```rust
impl Player {
    pub fn move_with_collision(
        &mut self,
        collision_system: &CollisionSystem,
        delta_time: f32,
        forward: bool,
        backward: bool,
        left: bool,
        right: bool,
    ) {
        let current_pos = self.position;
        let mut desired_pos = current_pos;

        if forward {
            let forward_x = self.yaw.to_radians().sin();
            let forward_z = self.yaw.to_radians().cos();
            desired_pos[0] -= forward_x * self.speed * delta_time;
            desired_pos[2] -= forward_z * self.speed * delta_time;
        }
        if backward {
            let forward_x = self.yaw.to_radians().sin();
            let forward_z = self.yaw.to_radians().cos();
            desired_pos[0] += forward_x * self.speed * delta_time;
            desired_pos[2] += forward_z * self.speed * delta_time;
        }
        if left {
            let right_x = self.yaw.to_radians().cos();
            let right_z = self.yaw.to_radians().sin();
            desired_pos[0] -= right_x * self.speed * delta_time;
            desired_pos[2] += right_z * self.speed * delta_time;
        }
        if right {
            let right_x = self.yaw.to_radians().cos();
            let right_z = self.yaw.to_radians().sin();
            desired_pos[0] += right_x * self.speed * delta_time;
            desired_pos[2] -= right_z * self.speed * delta_time;
        }

        self.position = collision_system.check_and_resolve_collision(current_pos, desired_pos);
    }
}
```

## System Workflow

1. **Initialization**: Build BVH from maze geometry
2. **Movement**: Player calculates desired position based on input
3. **Collision Detection**: Query BVH for potential collisions
4. **Collision Resolution**: Use vector projection for wall sliding
5. **Position Update**: Apply resolved position to player

## Performance Benefits

- **BVH Queries**: O(log n) average case vs O(n) brute force
- **Early Termination**: AABB tests reject most non-colliding geometry
- **Spatial Coherence**: Nearby objects are grouped together in the tree
- **Balanced Tree**: Median splits ensure good performance characteristics

This system provides efficient, realistic collision detection with smooth wall sliding for 3D maze navigation.
