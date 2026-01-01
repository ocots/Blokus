# API Guide - Blokus RL

Complete guide to the Blokus RL REST API.

**Version**: 2.0  
**Base URL**: `http://localhost:8000`  
**Last Updated**: 2026-01-01

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [Endpoints](#endpoints)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)
7. [Code Examples](#code-examples)
8. [Rate Limiting](#rate-limiting)

---

## Introduction

The Blokus RL API is a RESTful API built with FastAPI that provides programmatic access to the game engine. It allows you to:

- Create and manage games
- Execute moves
- Query game state
- List available AI models
- Interact with the game programmatically

### Key Features

✅ **RESTful Design**: Standard HTTP methods and status codes  
✅ **JSON Format**: All requests and responses use JSON  
✅ **Type Validation**: Pydantic models ensure data integrity  
✅ **Auto Documentation**: Interactive docs at `/docs`  
✅ **CORS Enabled**: Cross-origin requests supported  

---

## Getting Started

### Starting the Server

```bash
cd blokus-server
python main.py
```

Server starts on `http://localhost:8000`

### Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Quick Test

```bash
# Test the API is running
curl http://localhost:8000/

# Expected response:
# {"message": "Welcome to Blokus API"}
```

---

## Authentication

**Current Version**: No authentication required (local development only)

**Future Versions**: Will support JWT authentication for production deployments.

---

## Endpoints

### Root Endpoint

#### `GET /`

Welcome message and API status.

**Response**:
```json
{
  "message": "Welcome to Blokus API"
}
```

---

### Game Management

#### `POST /game/new`

Create a new game with optional player configurations.

**Request Body**:
```json
{
  "num_players": 4,
  "players": [
    {
      "name": "Alice",
      "type": "human",
      "persona": null
    },
    {
      "name": "Bot",
      "type": "ai",
      "persona": "random"
    }
  ],
  "start_player": 0
}
```

**Parameters**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `num_players` | int | No | 4 | Number of players (2-4) |
| `players` | array | No | null | Player configurations |
| `start_player` | int | No | 0 | Starting player index |

**Player Configuration**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Player display name |
| `type` | string | Yes | "human", "ai", or "shared" |
| `persona` | string | No | AI persona (for AI players) |

**Response**: [GameState](#gamestate)

**Example**:

```bash
curl -X POST http://localhost:8000/game/new \
  -H "Content-Type: application/json" \
  -d '{
    "num_players": 2,
    "players": [
      {"name": "Alice", "type": "human"},
      {"name": "Bot", "type": "ai", "persona": "random"}
    ],
    "start_player": 0
  }'
```

---

#### `GET /game/state`

Get the current game state.

**Response**: [GameState](#gamestate)

**Example**:

```bash
curl http://localhost:8000/game/state
```

---

#### `POST /game/move`

Execute a move in the game.

**Request Body**:
```json
{
  "player_id": 0,
  "piece_type": "I5",
  "orientation": 0,
  "row": 0,
  "col": 0
}
```

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `player_id` | int | Yes | Player making the move (0-3) |
| `piece_type` | string | Yes | Piece type (e.g., "I1", "L5") |
| `orientation` | int | Yes | Orientation index (0-7) |
| `row` | int | Yes | Row position (0-19) |
| `col` | int | Yes | Column position (0-19) |

**Response**: [MoveResponse](#moveresponse)

**Example**:

```bash
curl -X POST http://localhost:8000/game/move \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": 0,
    "piece_type": "I5",
    "orientation": 0,
    "row": 0,
    "col": 0
  }'
```

---

#### `POST /game/pass`

Pass the current player's turn.

**Response**: [GameState](#gamestate)

**Example**:

```bash
curl -X POST http://localhost:8000/game/pass
```

---

#### `POST /game/reset`

Reset the game to initial state.

**Response**: [GameState](#gamestate)

**Example**:

```bash
curl -X POST http://localhost:8000/game/reset
```

---

### AI Models

#### `GET /ai/models`

List all available AI models and personas.

**Response**:
```json
[
  {
    "id": "random",
    "name": "Aléatoire",
    "description": "Joue de manière totalement aléatoire",
    "level": "Débutant",
    "style": "Imprévisible",
    "tags": ["baseline", "random"],
    "enabled": true,
    "tooltip": "Parfait pour débuter"
  }
]
```

**Example**:

```bash
curl http://localhost:8000/ai/models
```

---

## Data Models

### GameState

Complete game state including board, players, and metadata.

```json
{
  "board": [[0, 0, ...], ...],
  "players": [
    {
      "id": 0,
      "name": "Alice",
      "color": "#3b82f6",
      "type": "human",
      "persona": null,
      "pieces_remaining": ["I1", "I2", ...],
      "pieces_count": 21,
      "squares_remaining": 89,
      "score": 0,
      "has_passed": false,
      "status": "playing",
      "display_name": "Alice",
      "turn_order": 0
    }
  ],
  "current_player_id": 0,
  "status": "in_progress",
  "turn_number": 0
}
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `board` | array | 20x20 grid (0=empty, 1-4=player colors) |
| `players` | array | Array of [PlayerState](#playerstate) |
| `current_player_id` | int | Current player index |
| `status` | string | "in_progress" or "finished" |
| `turn_number` | int | Current turn number |

---

### PlayerState

Individual player state.

```json
{
  "id": 0,
  "name": "Alice",
  "color": "#3b82f6",
  "type": "human",
  "persona": null,
  "pieces_remaining": ["I1", "I2", "I3", ...],
  "pieces_count": 21,
  "squares_remaining": 89,
  "score": 0,
  "has_passed": false,
  "status": "playing",
  "display_name": "Alice",
  "turn_order": 0
}
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Player ID (0-3) |
| `name` | string | Display name |
| `color` | string | Hex color code |
| `type` | string | "human", "ai", or "shared" |
| `persona` | string | AI persona (null for humans) |
| `pieces_remaining` | array | List of piece type names |
| `pieces_count` | int | Number of remaining pieces |
| `squares_remaining` | int | Total squares in remaining pieces |
| `score` | int | Current score |
| `has_passed` | bool | Has player passed? |
| `status` | string | "waiting", "playing", "passed", "finished" |
| `display_name` | string | Formatted display name |
| `turn_order` | int | Turn order position |

---

### MoveResponse

Response from a move attempt.

```json
{
  "success": true,
  "message": null,
  "game_state": { ... }
}
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Was the move successful? |
| `message` | string | Error message (if failed) |
| `game_state` | object | Updated [GameState](#gamestate) (if successful) |

---

### AIModelInfo

Information about an AI model.

```json
{
  "id": "random",
  "name": "Aléatoire",
  "description": "Joue de manière totalement aléatoire",
  "level": "Débutant",
  "style": "Imprévisible",
  "tags": ["baseline", "random"],
  "enabled": true,
  "tooltip": "Parfait pour débuter"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request data |
| 404 | Not Found | Game not initialized |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

#### Game Not Initialized

```json
{
  "detail": "Game not initialized"
}
```

**Solution**: Create a game first with `POST /game/new`

#### Invalid Move

```json
{
  "success": false,
  "message": "Invalid move according to Blokus rules"
}
```

**Solution**: Check move validity before submitting

#### Invalid Piece Type

```json
{
  "success": false,
  "message": "Invalid piece type: XYZ"
}
```

**Solution**: Use valid piece types (I1-I5, L3-L5, etc.)

---

## Code Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Create a new game
response = requests.post(f"{BASE_URL}/game/new", json={
    "num_players": 2,
    "players": [
        {"name": "Alice", "type": "human"},
        {"name": "Bot", "type": "ai", "persona": "random"}
    ],
    "start_player": 0
})
game_state = response.json()
print(f"Game created! Current player: {game_state['current_player_id']}")

# Get game state
response = requests.get(f"{BASE_URL}/game/state")
state = response.json()
print(f"Turn {state['turn_number']}, Player {state['current_player_id']}")

# Make a move
response = requests.post(f"{BASE_URL}/game/move", json={
    "player_id": 0,
    "piece_type": "I5",
    "orientation": 0,
    "row": 0,
    "col": 0
})
result = response.json()
if result["success"]:
    print("Move successful!")
else:
    print(f"Move failed: {result['message']}")

# Pass turn
response = requests.post(f"{BASE_URL}/game/pass")
state = response.json()
print(f"Turn passed. Next player: {state['current_player_id']}")
```

### JavaScript (Fetch API)

```javascript
const BASE_URL = 'http://localhost:8000';

// Create a new game
async function createGame() {
    const response = await fetch(`${BASE_URL}/game/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            num_players: 2,
            players: [
                { name: 'Alice', type: 'human' },
                { name: 'Bot', type: 'ai', persona: 'random' }
            ],
            start_player: 0
        })
    });
    const gameState = await response.json();
    console.log('Game created!', gameState);
    return gameState;
}

// Get game state
async function getGameState() {
    const response = await fetch(`${BASE_URL}/game/state`);
    const state = await response.json();
    console.log('Current state:', state);
    return state;
}

// Make a move
async function makeMove(playerId, pieceType, orientation, row, col) {
    const response = await fetch(`${BASE_URL}/game/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            player_id: playerId,
            piece_type: pieceType,
            orientation: orientation,
            row: row,
            col: col
        })
    });
    const result = await response.json();
    if (result.success) {
        console.log('Move successful!');
    } else {
        console.error('Move failed:', result.message);
    }
    return result;
}

// Pass turn
async function passTurn() {
    const response = await fetch(`${BASE_URL}/game/pass`, {
        method: 'POST'
    });
    const state = await response.json();
    console.log('Turn passed:', state);
    return state;
}

// Usage
createGame()
    .then(() => makeMove(0, 'I5', 0, 0, 0))
    .then(() => getGameState())
    .then(() => passTurn());
```

### JavaScript (Axios)

```javascript
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: { 'Content-Type': 'application/json' }
});

// Create game
const createGame = async () => {
    const { data } = await api.post('/game/new', {
        num_players: 2,
        players: [
            { name: 'Alice', type: 'human' },
            { name: 'Bot', type: 'ai', persona: 'random' }
        ]
    });
    return data;
};

// Make move
const makeMove = async (playerId, pieceType, orientation, row, col) => {
    const { data } = await api.post('/game/move', {
        player_id: playerId,
        piece_type: pieceType,
        orientation,
        row,
        col
    });
    return data;
};

// Get state
const getState = async () => {
    const { data } = await api.get('/game/state');
    return data;
};
```

### cURL Examples

```bash
# Create game
curl -X POST http://localhost:8000/game/new \
  -H "Content-Type: application/json" \
  -d '{"num_players": 2}'

# Get state
curl http://localhost:8000/game/state

# Make move
curl -X POST http://localhost:8000/game/move \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": 0,
    "piece_type": "I5",
    "orientation": 0,
    "row": 0,
    "col": 0
  }'

# Pass turn
curl -X POST http://localhost:8000/game/pass

# List AI models
curl http://localhost:8000/ai/models
```

---

## Rate Limiting

**Current Version**: No rate limiting

**Future Versions**: Will implement rate limiting for production:
- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## WebSocket Support

**Status**: Not yet implemented

**Planned**: Real-time game updates via WebSocket for multiplayer support.

---

## Versioning

**Current Version**: v1 (implicit)

**Future**: API versioning will be added:
- `/v1/game/new`
- `/v2/game/new`

---

## Best Practices

### 1. Check Game State Before Moves

```javascript
const state = await getGameState();
if (state.status === 'finished') {
    console.log('Game is over!');
    return;
}
```

### 2. Handle Errors Gracefully

```javascript
try {
    const result = await makeMove(0, 'I5', 0, 0, 0);
    if (!result.success) {
        console.error('Move rejected:', result.message);
    }
} catch (error) {
    console.error('API error:', error);
}
```

### 3. Validate Locally First

```javascript
// Check if piece is available
if (!player.pieces_remaining.includes(pieceType)) {
    console.error('Piece not available');
    return;
}

// Then make API call
await makeMove(playerId, pieceType, orientation, row, col);
```

---

## Troubleshooting

### Connection Refused

**Problem**: `Cannot connect to server at http://localhost:8000`

**Solution**:
1. Check if server is running: `ps aux | grep python`
2. Start server: `cd blokus-server && python main.py`
3. Check port availability: `lsof -i :8000`

### CORS Errors

**Problem**: CORS policy blocking requests

**Solution**: CORS is enabled for all origins in development. For production, configure allowed origins in `main.py`.

### Game Not Found

**Problem**: `Game not initialized`

**Solution**: Create a game first with `POST /game/new`

---

## Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Development Guide](development_guide.md)
- [Frontend Integration](../tutorials/frontend_customization.md)

---

**Next**: [Development Guide →](development_guide.md)
