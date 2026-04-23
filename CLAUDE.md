# Forge — Ultima-style Roguelike

A tile-based dungeon crawler written in Python/Pygame. Uses Tiled TMX maps for level data.

## Running the Game

```bash
python main.py
```

**Dependencies:** Python 3, Pygame 2.6  
**Config:** `config.ini` — window size (default 480×480)

> **Pygame version:** Target pygame 2.6 APIs throughout. When encountering code that uses deprecated or removed pygame patterns (e.g. `pygame.font.SysFont` size quirks, old `pygame.mask` usage, legacy event patterns), replace them with the current pygame 2.6 equivalents rather than preserving the old style.

## Controls

| Input | Action |
|---|---|
| Arrow keys / WASD | Move (discrete, one tile per key) |
| Hold Arrow / WASD | Move continuously (150ms repeat) |
| Right-click | Move toward mouse direction |
| Middle-click | Interact with tile (open/close doors) |
| ESC | Quit |

## Architecture

```
main.py           Entry point, creates Application and calls start()
game.py           Application — Pygame init, main game loop, input handling
dungeon.py        Dungeon, Tile, Entity, Door — world representation
player.py         Player, Viewport — character state and camera/FOV
mapparser.py      MapParser — parses Tiled TMX/TSX files into Python dicts
lib.py            Utilities: image loading, coordinate helpers, Direction enum
config.ini        Window dimensions
data/             Tilesets (PNG spritesheets + TSX definitions) and TMX maps
test/             Placeholder test suite (test_dungeon.py)
```

### Core Loop (`game.py:Application.start`)

Each frame at 60 FPS:
1. Clear screen
2. `dungeon.update()` / `player.update()` — currently stubs
3. `player.calculate_visibility(dungeon)` — recomputes FOV mask
4. `dungeon.draw()` / `player.draw()` — render
5. Process events (keyboard, mouse, quit)
6. Accumulated-time movement repeat (150ms threshold)

## Key Classes

### `Dungeon` (`dungeon.py`)
Holds a flat 1D array of `Tile` objects: index = `x + y * width`.  
Loads from `data/testroom.tmx` at startup via `MapParser`.  
`sloc` is the player spawn point read from the object layer.

### `Tile` (`dungeon.py`)
A 32×32 grid cell. Holds a base image (from dungeon tileset) and a list of
`Entity` objects layered on top. `is_passable()` is False if the tile property
says so, or if any entity on it is impassable.

### `Entity` / `Door` (`dungeon.py`)
`Entity` is the base for interactive objects. It carries an `animations` dict
mapping state names → Pygame surfaces, and a current `state` string.  
`Door` extends it: `is_passable()` returns `True` only when `state == "open"`;
`onclick()` toggles open/closed if the originator is within a 3×3 proximity.

### `Player` (`player.py`)
Tracks world-tile position and delegates camera work to `Viewport`.  
`try_move()` checks passability before committing a move.

### `Viewport` (`player.py`)
A `pygame.Rect` over world-tile coordinates representing the visible window
(15×15 tiles). Also owns a `pygame.Mask` for the FOV.  
`calculate_visibility()` implements a scanline flood-fill: starting from the
player's row it finds horizontal runs of passable tiles and propagates seed
points up/down, then expands the mask by one cell to reveal adjacent walls.

### `MapParser` (`mapparser.py`)
Reads Tiled's XML format. Tile layer data is base64 + zlib compressed; the
parser decodes it with `struct.unpack` into a list of GIDs.

### `lib.py`
- `load_image` — loads PNG with magenta (`0xff00ff`) as colour key
- `get_image_by_gid` / `get_object_images` — sprite extraction from sheets
- `get_direction` — converts screen angle to 8-way `Direction`
- `Direction` — plain class with 8 direction tuples (not an Enum)

## Data / Tilesets

| File | GID range | Contents |
|---|---|---|
| `dungeon.tsx` | 1–32 | Floor and wall tiles; `passable` property per tile |
| `objects.tsx` | 33–64 | Doors (open/closed), spawn marker; `state` and `objectid` properties |
| `characters.tsx` | 65+ | Character sprites (reserved) |

Map: `data/testroom.tmx` — 20×20 tiles, layers `RoomTiles` + `OverlayTiles` +
an object layer with 4 doors and 1 spawn point.

## Patterns in Use (Current)

| Pattern | Where |
|---|---|
| **Game Loop** | `game.py:Application.start` — fixed 60 FPS tick with accumulated-time repeat |
| **Update Method** | `Dungeon.update()` / `Player.update()` stubs ready for per-frame logic |
| **Component (partial)** | `Tile` owns a list of `Entity` objects; passability and drawing delegate to them |
| **Subclass / Template** | `Door` extends `Entity`, overrides `is_passable` and `onclick` |
| **Data-driven maps** | World defined in Tiled TMX/TSX files, not hard-coded |

## Good Starting Points for gameprogrammingpatterns.com

Adopt these patterns only when the problem they solve is actually felt — not speculatively. Each one adds surface area; earn it first.

- **Game Loop** (ch. 9) — already present; could add fixed timestep / variable rendering
- **Update Method** (ch. 10) — stubs exist; add NPC AI, animations
- **Dirty Flag** (ch. 11) — FOV recalculated every frame; recalculate only when player moves
- **Component** (ch. 14) — `Entity` list on `Tile` is a hint; grow into a full component system only if entity composition becomes complex
- **State Machine** (ch. 7) — `Door` state string is manual; a `StateMachine` class earns its keep once there are 3+ states or shared transitions
- **Observer** (ch. 4) — useful when the same event needs multiple independent reactions (logging, achievements, replay)
- **Flyweight** (ch. 3) — tile images reloaded per GID; worth sharing if profiling shows memory or load-time pressure
- **Spatial Partition** (ch. 20) — flat tile array is already a simple grid; useful only if entity count grows large enough to make linear scans measurable

## Architectural Direction

### KISS and evolutionary growth
Keep it simple. Every abstraction, layer, and pattern adds code surface area — more surface area means more places for bugs. Introduce structure only when the problem it solves is actually present, not in anticipation of future needs.

Architecture should evolve as the project grows: start with the simplest thing that works, refactor when real friction appears, and resist the urge to generalise from a single use case.

### Separation of concerns
The codebase should maintain clear boundaries between three layers, even as Pygame remains the current rendering backend:

- **Game logic** — pure computation: movement rules, FOV, entity state transitions, collision. No Pygame imports.
- **Display** — renders world state to screen. Reads game state; never mutates it.
- **Controller** — translates input events into intent (commands/actions) and forwards them to game logic.

New code should be placed in the layer it belongs to. Logic that bleeds across layers (e.g. input handling that also mutates entity state) should be flagged for refactoring.

### Game objects as data
Game object parameters (tile properties, entity stats, door behaviour, spawn locations) should be defined in data files, not hard-coded in Python. The existing TMX/TSX pipeline is the model to follow. When adding new object types or parameters, extend the data layer first and have the code read from it.

## Code Conventions

- **Functional style:** prefer pure functions with explicit inputs and outputs; relegate mutable state to IO boundaries (game loop, file I/O, Pygame surface writes)
- **Flat code:** avoid nesting beyond ~2–3 levels — use early returns and guard clauses instead of nested conditionals
- **Comments:** document intent and non-obvious constraints, never what the code does; a meaningful name beats a comment
- **Changes:** keep each change small and focused so it is easy to review; prefer surgical edits to existing code over rewrites unless the scope demands otherwise

## Notes

- Coordinate spaces: world = tile units; screen = pixels (1 tile = 32 px). `lib.py` has helpers.
- `mapparser.py` is standalone and has no Pygame dependency — good target for unit tests.
- The bare `except:` in `Application.start` swallows errors silently during development; worth narrowing.
- `Direction` is a plain class with class-level tuples, not a Python `Enum`. Moving to `enum.Enum` would add iteration and membership checks.
- **Known migration debt:** `Dungeon.draw()` and `Player.draw()` currently live on game-logic objects, violating the display-layer separation goal. Migrate display code to a dedicated renderer when touching those classes.
