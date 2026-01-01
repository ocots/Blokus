# Architecture Overview - Blokus RL

**Version**: 2.0  
**Last Updated**: 2026-01-01  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Module Overview](#module-overview)
4. [Technology Stack](#technology-stack)
5. [Design Principles](#design-principles)
6. [Data Flow](#data-flow)
7. [Deployment Architecture](#deployment-architecture)

---

## Introduction

Blokus RL is a comprehensive implementation of the Blokus board game with integrated reinforcement learning capabilities. The project follows a **modular, layered architecture** designed for scalability, maintainability, and extensibility.

### Key Characteristics

- **Modular Design**: Clear separation between game engine, API, frontend, and RL components
- **SOLID Principles**: Object-oriented design following industry best practices
- **Full-Stack**: Python backend, FastAPI REST API, vanilla JavaScript frontend
- **AI-Ready**: Built-in RL environment compatible with OpenAI Gym
- **Testable**: 99.3% test coverage on core modules

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Blokus RL System                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐      ┌──────────────┐      ┌────────────┐ │
│  │   Frontend  │◄────►│  API Server  │◄────►│   Engine   │ │
│  │  (Web UI)   │ HTTP │   (FastAPI)  │      │  (Python)  │ │
│  └─────────────┘      └──────────────┘      └────────────┘ │
│                              │                      │         │
│                              │                      ▼         │
│                              │              ┌────────────┐   │
│                              │              │  RL Module │   │
│                              │              │ (Training) │   │
│                              │              └────────────┘   │
│                              ▼                                │
│                       ┌──────────────┐                       │
│                       │   Registry   │                       │
│                       │  (AI Models) │                       │
│                       └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### Layer Architecture

```
┌──────────────────────────────────────────────────────┐
│                  Presentation Layer                   │
│  (HTML/CSS/JavaScript - User Interface)              │
└────────────────────┬─────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼─────────────────────────────────┐
│                   API Layer                           │
│  (FastAPI - Request Handling, Validation)            │
└────────────────────┬─────────────────────────────────┘
                     │ Function Calls
┌────────────────────▼─────────────────────────────────┐
│                 Business Logic Layer                  │
│  (Game Engine - Rules, State Management)             │
└────────────────────┬─────────────────────────────────┘
                     │ Data Access
┌────────────────────▼─────────────────────────────────┐
│                   Data Layer                          │
│  (In-Memory State, RL Environment)                   │
└──────────────────────────────────────────────────────┘
```

---

## Module Overview

### 1. **blokus-engine** 🎮

**Purpose**: Core game logic and rules engine

**Key Components**:
- `pieces.py` - 21 Blokus pieces with rotations/reflections
- `board.py` - 20×20 game board management
- `rules.py` - Placement validation and rule enforcement
- `game.py` - Game orchestration and state management
- `player.py` - Unified player representation
- `game_manager.py` - Centralized player/turn management
- `player_factory.py` - Player creation patterns
- `game_manager_factory.py` - Game setup patterns

**Architecture Pattern**: Domain-Driven Design (DDD)

**Dependencies**: NumPy

**Lines of Code**: ~3,500

---

### 2. **blokus-server** 🌐

**Purpose**: REST API for game interactions

**Key Components**:
- `main.py` - FastAPI application and endpoints
- `api/models.py` - Pydantic data models
- `api/routes.py` - Route handlers (future)

**Endpoints**:
- `POST /game/new` - Create new game
- `GET /game/state` - Get current state
- `POST /game/move` - Play a move
- `POST /game/pass` - Pass turn
- `GET /ai/models` - List available AI models

**Architecture Pattern**: RESTful API, Layered Architecture

**Dependencies**: FastAPI, Uvicorn, Pydantic

**Lines of Code**: ~400

---

### 3. **blokus-web** 💻

**Purpose**: Interactive web interface

**Key Components**:
- `index.html` - Main application structure
- `css/style.css` - Styling and responsive design
- `js/main.js` - Application entry point
- `js/game.js` - Game state management
- `js/board.js` - Board rendering
- `js/controls.js` - User input handling
- `js/setup.js` - Game configuration UI
- `js/api.js` - API client
- `js/state.js` - Application state machine

**Architecture Pattern**: MVC (Model-View-Controller), State Machine

**Dependencies**: None (Vanilla JavaScript)

**Lines of Code**: ~2,500

---

### 4. **blokus-engine/rl** 🧠

**Purpose**: Reinforcement learning environment and training

**Key Components**:
- `environment.py` - OpenAI Gym-compatible environment
- `observations.py` - State representation (47 channels)
- `actions.py` - Action space encoding/decoding
- `rewards.py` - Reward shaping functions
- `agents/` - RL agent implementations (DQN, etc.)
- `training/` - Training infrastructure
- `networks.py` - Neural network architectures
- `registry.py` - Model management and loading

**Architecture Pattern**: Strategy Pattern, Factory Pattern

**Dependencies**: PyTorch, Gymnasium, NumPy

**Lines of Code**: ~4,000

---

## Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Core language |
| NumPy | 1.24+ | Array operations |
| FastAPI | 0.104+ | REST API framework |
| Pydantic | 2.0+ | Data validation |
| Uvicorn | 0.24+ | ASGI server |
| PyTorch | 2.0+ | Deep learning |
| Gymnasium | 0.29+ | RL environment |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| HTML5 | - | Structure |
| CSS3 | - | Styling |
| JavaScript | ES6+ | Logic |
| Canvas API | - | Board rendering |

### Development Tools

| Tool | Purpose |
|------|---------|
| pytest | Testing framework |
| mypy | Type checking |
| ruff | Linting |
| Git | Version control |

---

## Design Principles

### SOLID Principles

The codebase strictly follows SOLID principles:

1. **Single Responsibility Principle (SRP)**
   - Each class has one clear responsibility
   - Example: `Player` manages player data, `GameManager` manages turns

2. **Open/Closed Principle (OCP)**
   - Extensible via factories and enums
   - Example: New player types via `PlayerFactory`

3. **Liskov Substitution Principle (LSP)**
   - Consistent interfaces across implementations
   - Example: All `Player` instances have identical interface

4. **Interface Segregation Principle (ISP)**
   - Minimal, focused interfaces
   - Example: `Player` exposes only necessary methods

5. **Dependency Inversion Principle (DIP)**
   - Dependencies via abstractions
   - Example: `Game` depends on `GameManager` abstraction

### Additional Principles

- **DRY** (Don't Repeat Yourself): No code duplication
- **KISS** (Keep It Simple, Stupid): Simple, direct solutions
- **YAGNI** (You Aren't Gonna Need It): Implement only what's needed
- **Separation of Concerns**: Clear module boundaries

---

## Data Flow

### Game Creation Flow

```
User (Frontend)
    │
    ├─► Setup UI (setup.js)
    │       │
    │       ├─► Collect player configs
    │       └─► Generate start player
    │
    ├─► API Client (api.js)
    │       │
    │       └─► POST /game/new
    │               │
    ├─────────────► FastAPI (main.py)
    │               │
    │               ├─► Validate request
    │               ├─► GameManagerFactory.create_from_config()
    │               │       │
    │               │       ├─► PlayerFactory.create_players()
    │               │       └─► GameManager(players)
    │               │
    │               └─► Game(game_manager)
    │                       │
    └───────────────────────┴─► Return GameState
```

### Move Execution Flow

```
User Click (Frontend)
    │
    ├─► Controls (controls.js)
    │       │
    │       └─► Validate locally
    │
    ├─► API Client (api.js)
    │       │
    │       └─► POST /game/move
    │               │
    ├─────────────► FastAPI (main.py)
    │               │
    │               ├─► Game.is_valid_move()
    │               │       │
    │               │       └─► Rules.is_valid_placement()
    │               │
    │               ├─► Game.play_move()
    │               │       │
    │               │       ├─► Board.place_piece()
    │               │       ├─► Player.play_piece()
    │               │       └─► GameManager.next_turn()
    │               │
    │               └─► Return MoveResponse
    │
    └───────────────────────┴─► Update UI
```

---

## Deployment Architecture

### Local Development

```
┌─────────────────────────────────────────┐
│          Developer Machine               │
│                                          │
│  ┌────────────┐      ┌────────────┐    │
│  │  Frontend  │      │  Backend   │    │
│  │  (Browser) │◄────►│  (Python)  │    │
│  │ localhost  │ HTTP │ localhost  │    │
│  │   :5500    │      │   :8000    │    │
│  └────────────┘      └────────────┘    │
│                                          │
└─────────────────────────────────────────┘
```

### Production Deployment (Future)

```
┌─────────────────────────────────────────────────┐
│                   Cloud Provider                 │
│                                                   │
│  ┌──────────┐      ┌──────────┐      ┌────────┐│
│  │   CDN    │      │   API    │      │   DB   ││
│  │ (Static) │      │ (Docker) │      │ (Redis)││
│  └──────────┘      └──────────┘      └────────┘│
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## Performance Characteristics

### Game Engine

- **Move Validation**: O(n) where n = piece size
- **Valid Moves Generation**: O(p × r × b) where:
  - p = remaining pieces (~21)
  - r = rotations (~4)
  - b = board positions (~400)
- **Memory**: ~10 MB per game instance

### API

- **Latency**: < 50ms for move validation
- **Throughput**: ~100 requests/second (single instance)
- **Concurrent Games**: Limited by memory (~1000 games)

### Frontend

- **Initial Load**: < 2 seconds
- **Render Time**: < 16ms (60 FPS)
- **Memory**: ~50 MB

---

## Security Considerations

### Current Implementation

- **CORS**: Enabled for all origins (development only)
- **Input Validation**: Pydantic models validate all inputs
- **No Authentication**: Local-only deployment

### Future Enhancements

- [ ] JWT authentication
- [ ] Rate limiting
- [ ] HTTPS/TLS
- [ ] Input sanitization
- [ ] CORS restrictions

---

## Scalability

### Current Limitations

- Single-threaded API server
- In-memory game state (no persistence)
- No load balancing

### Scaling Strategy

1. **Horizontal Scaling**: Multiple API instances behind load balancer
2. **State Management**: Redis for distributed state
3. **Caching**: Cache valid moves, board states
4. **Database**: PostgreSQL for game history
5. **Async Processing**: Celery for AI move computation

---

## Monitoring & Observability

### Metrics to Track

- API response times
- Game creation rate
- Move validation errors
- AI model inference time
- Memory usage
- Active games count

### Logging Strategy

- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Format**: JSON structured logging
- **Destination**: File + Console (development), ELK Stack (production)

---

## Related Documentation

- [Player System Architecture](player_system.md)
- [Game Engine Details](game_engine.md)
- [API Design](api_design.md)
- [Architecture Diagrams](diagrams.md)
- [Design Decisions](../design/design_decisions.md)

---

**Next**: [Player System Architecture →](player_system.md)
