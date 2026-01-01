# Player System Architecture

**Version**: 2.0  
**Last Updated**: 2026-01-01  
**Author**: Blokus RL Team

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Design](#architecture-design)
3. [Core Components](#core-components)
4. [Class Diagrams](#class-diagrams)
5. [Interaction Patterns](#interaction-patterns)
6. [Implementation Details](#implementation-details)
7. [Usage Examples](#usage-examples)

---

## Overview

The **Player System** is a unified architecture for managing players and game turns in Blokus RL. Implemented in January 2026, it replaces the fragmented player management with a centralized, SOLID-compliant design.

### Key Features

✅ **Unified Player Representation**: Single `Player` class for all player types  
✅ **Centralized Turn Management**: `GameManager` handles all turn logic  
✅ **Factory Patterns**: Easy creation of players and game configurations  
✅ **Type Safety**: Enums for player types, statuses, and game states  
✅ **Extensibility**: Easy to add new player types or behaviors  
✅ **Full Test Coverage**: 123 tests covering all scenarios  

### Design Goals

1. **Eliminate Fragmentation**: Consolidate player logic in one place
2. **Follow SOLID Principles**: Clean, maintainable architecture
3. **Support All Player Types**: Human, AI, Shared (3-player mode)
4. **Enable State Machines**: Foundation for future state machine implementation
5. **Maintain Backward Compatibility**: Existing code continues to work

---

## Architecture Design

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Player System                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐      ┌──────────────┐                │
│  │ PlayerTypes  │      │    Player    │                │
│  │   (Enums)    │─────►│   (Class)    │                │
│  └──────────────┘      └──────┬───────┘                │
│                               │                          │
│                               │ manages                  │
│                               ▼                          │
│                        ┌──────────────┐                 │
│                        │ GameManager  │                 │
│                        │   (Class)    │                 │
│                        └──────┬───────┘                 │
│                               │                          │
│                               │ uses                     │
│                               ▼                          │
│  ┌──────────────┐      ┌──────────────┐                │
│  │PlayerFactory │      │GameManager   │                │
│  │   (Class)    │      │   Factory    │                │
│  └──────────────┘      └──────────────┘                │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Layered Architecture

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│  (Game, API, Frontend)                  │
└────────────────┬────────────────────────┘
                 │ uses
┌────────────────▼────────────────────────┐
│         Factory Layer                   │
│  (PlayerFactory, GameManagerFactory)    │
└────────────────┬────────────────────────┘
                 │ creates
┌────────────────▼────────────────────────┐
│         Domain Layer                    │
│  (Player, GameManager)                  │
└────────────────┬────────────────────────┘
                 │ uses
┌────────────────▼────────────────────────┐
│         Type Layer                      │
│  (PlayerType, PlayerStatus, etc.)       │
└─────────────────────────────────────────┘
```

---

## Core Components

### 1. PlayerTypes (Enums)

**File**: `blokus-engine/src/blokus/player_types.py`

Defines all enums used in the player system:

#### PlayerType

```python
class PlayerType(Enum):
    HUMAN = "human"      # Human player
    AI = "ai"            # AI player
    SHARED = "shared"    # Shared player (3-player mode)
```

#### PlayerStatus

```python
class PlayerStatus(Enum):
    WAITING = "waiting"    # Waiting for turn
    PLAYING = "playing"    # Currently playing
    PASSED = "passed"      # Has passed
    FINISHED = "finished"  # Game finished
```

#### Additional Enums

- `GameState`: Overall game state
- `TurnState`: Turn-specific state
- `MoveState`: Move validation state
- `UIState`: UI state (for future state machines)

**Purpose**: Type safety, clear semantics, extensibility

---

### 2. Player Class

**File**: `blokus-engine/src/blokus/player.py`

Unified player representation with all necessary data and behavior.

#### Structure

```python
@dataclass
class Player:
    # === IDENTITY ===
    id: int                           # Unique player ID (0-3)
    name: str                         # Display name
    color: str                        # Hex color (#3b82f6)
    type: PlayerType                  # Human/AI/Shared
    persona: Optional[str] = None     # AI persona (random, aggressive, etc.)
    
    # === GAME STATE ===
    remaining_pieces: Set[PieceType]  # Available pieces
    has_passed: bool = False          # Has player passed?
    last_piece_was_monomino: bool = False
    
    # === METADATA ===
    status: PlayerStatus = PlayerStatus.WAITING
    score: int = 0
    turn_order: Optional[int] = None
```

#### Key Methods

| Method | Purpose |
|--------|---------|
| `play_piece(piece_type)` | Mark piece as played |
| `pass_turn()` | Mark player as passed |
| `calculate_score()` | Calculate final score |
| `to_dict()` | Serialize to dictionary |
| `from_dict(data)` | Deserialize from dictionary |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_human` | bool | Is this a human player? |
| `is_ai` | bool | Is this an AI player? |
| `is_shared` | bool | Is this a shared player? |
| `display_name` | str | Formatted display name |
| `pieces_count` | int | Number of remaining pieces |
| `squares_remaining` | int | Total squares in remaining pieces |

**Design Pattern**: Data Class with behavior

---

### 3. GameManager Class

**File**: `blokus-engine/src/blokus/game_manager.py`

Centralized manager for player order and turn management.

#### Responsibilities

1. **Player Management**: Maintain ordered list of players
2. **Turn Management**: Handle turn transitions
3. **State Tracking**: Track current player, turn history
4. **Game State**: Determine game over, winners, rankings

#### Structure

```python
@dataclass
class GameManager:
    players: List[Player]
    current_player_index: int = 0
    turn_history: List[int] = field(default_factory=list)
    game_finished: bool = False
```

#### Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `next_turn()` | Advance to next player | Player |
| `is_game_over()` | Check if game finished | bool |
| `get_winner()` | Get winning player | Optional[Player] |
| `get_rankings()` | Get player rankings | Dict[int, int] |
| `get_play_order()` | Get players in play order | List[Player] |
| `get_score_order()` | Get players by score | List[Player] |

#### Turn Advancement Algorithm

```python
def next_turn(self) -> Player:
    # 1. Mark current player as waiting
    self.current_player.status = PlayerStatus.WAITING
    
    # 2. Add to history
    self.turn_history.append(self.current_player_index)
    
    # 3. Find next active player
    attempts = 0
    while attempts < len(self.players):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        next_player = self.players[self.current_player_index]
        
        if not next_player.has_passed:
            next_player.status = PlayerStatus.PLAYING
            return next_player
        
        attempts += 1
    
    # 4. All players passed - game over
    self.game_finished = True
    return self.players[self.current_player_index]
```

**Design Pattern**: Manager Pattern, Iterator Pattern

---

### 4. PlayerFactory Class

**File**: `blokus-engine/src/blokus/player_factory.py`

Factory for creating players with standard configurations.

#### Methods

```python
class PlayerFactory:
    @classmethod
    def create_human_player(cls, id: int, name: str, color: str = None) -> Player
    
    @classmethod
    def create_ai_player(cls, id: int, persona: str = "random", color: str = None) -> Player
    
    @classmethod
    def create_shared_player(cls, id: int, color: str = None) -> Player
    
    @classmethod
    def create_players_from_config(cls, configs: List[Dict]) -> List[Player]
    
    @classmethod
    def create_standard_players(cls, num_players: int) -> List[Player]
```

#### Default Colors

```python
DEFAULT_COLORS = [
    "#3b82f6",  # Blue
    "#22c55e",  # Green
    "#eab308",  # Yellow
    "#ef4444"   # Red
]
```

**Design Pattern**: Factory Method Pattern

---

### 5. GameManagerFactory Class

**File**: `blokus-engine/src/blokus/game_manager_factory.py`

Factory for creating GameManager instances with various configurations.

#### Methods

```python
class GameManagerFactory:
    @classmethod
    def create_from_config(cls, player_configs: List[Dict], starting_player_id: int = 0) -> GameManager
    
    @classmethod
    def create_standard_game(cls, num_players: int = 4, starting_player_id: int = 0) -> GameManager
    
    @classmethod
    def create_ai_game(cls, ai_configs: List[Dict], starting_player_id: int = 0) -> GameManager
    
    @classmethod
    def create_mixed_game(cls, num_humans: int, num_ais: int, ai_personas: List[str] = None, starting_player_id: int = 0) -> GameManager
```

**Design Pattern**: Abstract Factory Pattern

---

## Class Diagrams

### Player System Class Diagram

```
┌─────────────────────┐
│   PlayerType        │
│   <<enumeration>>   │
├─────────────────────┤
│ + HUMAN             │
│ + AI                │
│ + SHARED            │
└─────────────────────┘
         △
         │ uses
         │
┌────────┴────────────────────────────────────┐
│              Player                          │
├──────────────────────────────────────────────┤
│ - id: int                                    │
│ - name: str                                  │
│ - color: str                                 │
│ - type: PlayerType                           │
│ - persona: Optional[str]                     │
│ - remaining_pieces: Set[PieceType]           │
│ - has_passed: bool                           │
│ - status: PlayerStatus                       │
│ - score: int                                 │
├──────────────────────────────────────────────┤
│ + play_piece(piece_type: PieceType): void   │
│ + pass_turn(): void                          │
│ + calculate_score(): int                     │
│ + to_dict(): Dict                            │
│ + from_dict(data: Dict): Player              │
├──────────────────────────────────────────────┤
│ + is_human: bool                             │
│ + is_ai: bool                                │
│ + is_shared: bool                            │
│ + display_name: str                          │
└──────────────────────────────────────────────┘
         △
         │ manages
         │
┌────────┴────────────────────────────────────┐
│           GameManager                        │
├──────────────────────────────────────────────┤
│ - players: List[Player]                      │
│ - current_player_index: int                  │
│ - turn_history: List[int]                    │
│ - game_finished: bool                        │
├──────────────────────────────────────────────┤
│ + next_turn(): Player                        │
│ + is_game_over(): bool                       │
│ + get_winner(): Optional[Player]             │
│ + get_rankings(): Dict[int, int]             │
│ + get_play_order(): List[Player]             │
│ + to_dict(): Dict                            │
└──────────────────────────────────────────────┘
         △
         │ creates
         │
┌────────┴────────────────────────────────────┐
│        GameManagerFactory                    │
├──────────────────────────────────────────────┤
│ + create_from_config(...)                   │
│ + create_standard_game(...)                 │
│ + create_ai_game(...)                       │
│ + create_mixed_game(...)                    │
└──────────────────────────────────────────────┘
```

---

## Interaction Patterns

### Creating a Standard Game

```python
# Using GameManagerFactory
game_manager = GameManagerFactory.create_standard_game(
    num_players=4,
    starting_player_id=0
)

# Players are automatically created with default names and colors
# GameManager is ready to use
game = Game(game_manager=game_manager)
```

### Creating a Custom Game

```python
# Define player configurations
player_configs = [
    {"id": 0, "name": "Alice", "type": "human"},
    {"id": 1, "type": "ai", "persona": "aggressive"},
    {"id": 2, "name": "Bob", "type": "human"},
    {"id": 3, "type": "ai", "persona": "defensive"}
]

# Create GameManager from config
game_manager = GameManagerFactory.create_from_config(
    player_configs,
    starting_player_id=1  # AI starts
)

game = Game(game_manager=game_manager)
```

### Turn Management

```python
# Get current player
current = game_manager.current_player
print(f"Current player: {current.display_name}")

# Player makes a move
current.play_piece(PieceType.I5)

# Advance to next turn
next_player = game_manager.next_turn()
print(f"Next player: {next_player.display_name}")

# Check if game is over
if game_manager.is_game_over():
    winner = game_manager.get_winner()
    if winner:
        print(f"Winner: {winner.display_name}")
    else:
        print("Tie game!")
```

---

## Implementation Details

### SOLID Principles Applied

#### Single Responsibility Principle (SRP)

- `Player`: Manages player data only
- `GameManager`: Manages turns only
- `PlayerFactory`: Creates players only
- `GameManagerFactory`: Creates game managers only

#### Open/Closed Principle (OCP)

- New player types can be added via `PlayerType` enum
- New AI personas don't require code changes
- Factories handle creation logic, extensible without modification

#### Liskov Substitution Principle (LSP)

- All `Player` instances have identical interface
- Human, AI, and Shared players are interchangeable

#### Interface Segregation Principle (ISP)

- `Player` exposes only necessary methods
- No bloated interfaces

#### Dependency Inversion Principle (DIP)

- `Game` depends on `GameManager` (abstraction)
- `GameManager` depends on `Player` (abstraction)
- No direct dependencies on concrete implementations

### Design Patterns Used

1. **Factory Method Pattern**: `PlayerFactory`, `GameManagerFactory`
2. **Data Class Pattern**: `Player`, `GameManager`
3. **Manager Pattern**: `GameManager`
4. **Strategy Pattern**: Different player types (future AI strategies)
5. **Enum Pattern**: Type-safe constants

---

## Usage Examples

### Example 1: 4-Player Standard Game

```python
from blokus.game_manager_factory import GameManagerFactory
from blokus.game import Game

# Create standard 4-player game
game_manager = GameManagerFactory.create_standard_game(4)
game = Game(game_manager=game_manager)

# Players: Joueur 1, Joueur 2, Joueur 3, Joueur 4
# Colors: Blue, Green, Yellow, Red
# All human players
```

### Example 2: Mixed Human/AI Game

```python
# 2 humans, 2 AIs
game_manager = GameManagerFactory.create_mixed_game(
    num_humans=2,
    num_ais=2,
    ai_personas=["random", "aggressive"]
)
game = Game(game_manager=game_manager)

# Players:
# - Joueur 1 (Human, Blue)
# - Joueur 2 (Human, Green)
# - Random AI (Yellow)
# - Aggressive AI (Red)
```

### Example 3: 3-Player Game with Shared Player

```python
player_configs = [
    {"id": 0, "name": "Alice", "type": "human"},
    {"id": 1, "name": "Bob", "type": "human"},
    {"id": 2, "name": "Charlie", "type": "human"},
    {"id": 3, "type": "shared"}  # Shared 4th player
]

game_manager = GameManagerFactory.create_from_config(player_configs)
game = Game(game_manager=game_manager)

# The shared player is controlled by the 3 human players in rotation
```

### Example 4: Accessing Player Information

```python
# Get all players
for player in game_manager.players:
    print(f"{player.display_name} ({player.type.value})")
    print(f"  Pieces: {player.pieces_count}")
    print(f"  Score: {player.score}")
    print(f"  Status: {player.status.value}")

# Get current player
current = game_manager.current_player
print(f"\nCurrent turn: {current.display_name}")

# Get players by score
rankings = game_manager.get_score_order()
print("\nLeaderboard:")
for i, player in enumerate(rankings, 1):
    print(f"{i}. {player.display_name}: {player.score} points")
```

---

## Testing

### Test Coverage

- **player_types.py**: 19 tests
- **player.py**: 28 tests
- **player_factory.py**: 16 tests
- **game_manager.py**: 42 tests
- **game_manager_factory.py**: 18 tests

**Total**: 123 tests, 100% coverage

### Test Categories

1. **Unit Tests**: Individual class methods
2. **Integration Tests**: Component interactions
3. **Edge Cases**: Boundary conditions, error handling
4. **Serialization Tests**: to_dict/from_dict roundtrips

---

## Performance

### Benchmarks

| Operation | Time | Memory |
|-----------|------|--------|
| Create Player | < 1μs | 1 KB |
| Create GameManager | < 10μs | 5 KB |
| next_turn() | < 5μs | 0 KB |
| get_rankings() | < 20μs | 1 KB |

### Scalability

- **Players**: Supports 2-4 players (game constraint)
- **Turn History**: O(n) space where n = total turns
- **Memory**: ~10 KB per game instance

---

## Migration Guide

### From Old to New Architecture

**Old Code**:
```python
# Old way - direct player creation
players = [Player(id=i) for i in range(4)]
game = Game(players=players)
```

**New Code**:
```python
# New way - using factories
game_manager = GameManagerFactory.create_standard_game(4)
game = Game(game_manager=game_manager)
```

### Backward Compatibility

The `Game` class maintains backward compatibility:

```python
# Still works - creates default GameManager internally
game = Game(num_players=4)

# Access via properties
game.players          # List[Player]
game.current_player   # Player
game.num_players      # int
```

---

## Future Enhancements

### Planned Features

- [ ] State Machine Integration (PlayerStateMachine)
- [ ] Event System (player events, observers)
- [ ] Undo/Redo Support
- [ ] Player Statistics Tracking
- [ ] Replay System

### Extensibility Points

1. **New Player Types**: Add to `PlayerType` enum
2. **New AI Personas**: Add to `PlayerFactory`
3. **Custom Scoring**: Override `calculate_score()`
4. **Custom Turn Logic**: Extend `GameManager.next_turn()`

---

## Related Documentation

- [Architecture Overview](overview.md)
- [Game Engine Details](game_engine.md)
- [API Design](api_design.md)
- [Development Guide](../guides/development_guide.md)

---

**Next**: [Game Engine Architecture →](game_engine.md)
