# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

2D N-body space simulation with soft-body physics, built on pygame. Bodies interact via gravity, repulsion, springs, and spontaneous merging. The simulation supports composite bodies (groups of bodies connected by springs), dynamic spring formation, and configurable merge conditions.

## Running

```bash
python main.py
```

Dependencies: `pygame`, `numpy`, `scipy`, `networkx`. No requirements.txt or pyproject.toml exists yet — install manually.

## Architecture

**MVC with Event Bus** — The codebase follows Model-View-Controller with a publish/subscribe EventBus for decoupled communication between layers.

### Simulation Loop (main.py)

Each frame:
1. Reset forces on all bodies
2. Build Barnes-Hut quadtree
3. Compute gravity (long-range, via BH approximation)
4. Compute neighborhood pairs (short-range, via quadtree proximity query)
5. Compute local forces (repulsion, collision damping) on neighborhood pairs
6. Virtual spring field: dynamically connect slow, nearby bodies with springs
7. Spontaneous merging: merge overlapping bodies meeting configurable conditions
8. Update springs (apply spring forces, break overstressed springs)
9. Update body positions (Verlet integration)
10. Reconstruct composite bodies from spring-connected components (networkx)
11. Render

### Key Design Patterns

**Force generators (model/forces.py)** — Forces are closures returned by factory functions (`generate_gravitational_force`, `generate_repulsion_force`, etc.). Each factory captures parameters and returns a `Callable[[Body, Body], vec2]` that the Barnes-Hut tree evaluates on body pairs.

**Composable conditions (model/condition.py)** — `Condition` objects wrap `(Body, Body) -> bool` predicates and support `&`, `|`, `~` operators. Used by `MergeCondition` factory (model/merge_condition.py) to build complex merge criteria declaratively.

**Verlet integration (model/body.py)** — Bodies store `_pos` and `_old_pos`; velocity is derived as `(pos - old_pos) / dt`. The `update()` method implements position-Verlet: `x(t+dt) = 2x(t) - x(t-dt) + a*dt²`. This is a symplectic integrator that conserves energy well.

**Barnes-Hut (model/bh.py)** — Quadtree-based O(n log n) gravity. Also used for spatial queries: `compute_neighborhood_pairs` finds all body pairs within a threshold distance, which feeds local forces, virtual springs, and merge logic.

**Transient composites** — `CompositeBody` (model/composite_body.py) is reconstructed each frame from spring connectivity graphs (via `springs.find_composite_bodies()` using networkx connected components). It provides aggregate physics: center of mass, angular momentum, moment of inertia, rotational/internal energy decomposition.

**SimState singleton** — Global simulation time and pause state, accessed via `SimState()`.

### Directory Layout

- `model/` — Physics: Body, BodyList, Springs, BarnesHut, CompositeBody, forces, merge conditions, virtual spring field, convex hull
- `view/` — Rendering: Renderer (pan/zoom viewport), draw functions (bodies, springs, hulls, quadtree)
- `controller/` — Input handling: state machine (idle, dragging, panning)
- `events/` — EventBus pub/sub, handler registration
- `utils/` — Constants, body factories, circle geometry tools, spring mesh generation
- `audio/` — Audio manager/queue (currently disabled)
- `ai/` — Agent stubs (subsumption architecture, not yet integrated)
- `experimental/` — SoA (Structure of Arrays) prototype for future GPU migration
- `test/` — Benchmarks (`bm*.py`) and live visual tests (`live*.py`), not a formal test suite

## Physics Conventions

- Units are simulation units (not SI). Gravity constant is `NEWTON_UNIV_GRAVITY * 1e7`.
- Body radius scales as `mass^(1/3)`.
- Springs are tuples: `(body1, body2, stiffness, damping, equilibrium, break_distance_factor, break_force)`. Accessed via `Spring` static methods with index constants.
- Local forces (repulsion, damping) only act between neighborhood pairs found by the quadtree, not all-pairs.

## Active Development Directions

- SoA data layout for GPU compute (experimental/SoA.py — the transition is in progress per git history)
- Delaunay triangulation for composite body links (TODO)
- cupy-based quadtree (TODO)
