# Quick Start Guide - Blokus RL

Get up and running with Blokus RL in 5 minutes!

---

## 🎯 What You'll Learn

- Install and setup Blokus RL
- Start your first game
- Make moves via API
- Understand the basic workflow

**Time Required**: 5 minutes  
**Difficulty**: Beginner

---

## Prerequisites

- **Python 3.10+** installed
- **Git** installed
- Basic command line knowledge

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/ocots/Blokus.git
cd Blokus
```

---

## Step 2: Setup Backend

```bash
# Navigate to engine
cd blokus-engine

# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e ".[dev]"

# Verify installation
pytest tests/ -v
```

**Expected**: All tests pass ✅

---

## Step 3: Start the API Server

```bash
# Open a new terminal
cd blokus-server

# Start server
python main.py
```

**Expected Output**:
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Server is now running! 🚀

---

## Step 4: Open the Web Interface

```bash
# Open another terminal
cd blokus-web

# Start simple HTTP server
python -m http.server 5500
```

**Open in browser**: http://localhost:5500

You should see the Blokus game interface! 🎮

---

## Step 5: Play Your First Game

### Via Web Interface

1. **Click "Nouvelle Partie"**
2. **Configure players**:
   - Number of players: 2-4
   - Names and types (Human/AI)
3. **Click "Démarrer"**
4. **Play**:
   - Click a piece in your inventory
   - Rotate with R/S keys
   - Click on board to place
   - Click "Passer" to pass turn

### Via API (Python)

```python
import requests

BASE_URL = "http://localhost:8000"

# Create game
response = requests.post(f"{BASE_URL}/game/new", json={
    "num_players": 2
})
print("Game created!")

# Get state
state = requests.get(f"{BASE_URL}/game/state").json()
print(f"Current player: {state['current_player_id']}")

# Make a move
move = requests.post(f"{BASE_URL}/game/move", json={
    "player_id": 0,
    "piece_type": "I5",
    "orientation": 0,
    "row": 0,
    "col": 0
}).json()

if move["success"]:
    print("Move successful! ✅")
else:
    print(f"Move failed: {move['message']}")
```

### Via API (cURL)

```bash
# Create game
curl -X POST http://localhost:8000/game/new \
  -H "Content-Type: application/json" \
  -d '{"num_players": 2}'

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
```

---

## Step 6: Explore the API

Visit the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Try the endpoints directly in your browser! 🔍

---

## Common Issues

### Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Module Not Found

**Problem**: `ModuleNotFoundError: No module named 'blokus'`

**Solution**:
```bash
# Make sure you're in virtual environment
source .venv/bin/activate

# Reinstall
pip install -e .
```

### Tests Failing

**Problem**: Some tests fail

**Solution**:
```bash
# Run specific test to see error
pytest tests/test_game.py -v --tb=short

# Check Python version
python --version  # Should be 3.10+
```

---

## Next Steps

Now that you're set up, explore more:

### 📚 Learn More

- **[Architecture Overview](../architecture/overview.md)**: Understand the system
- **[API Guide](../guides/api_guide.md)**: Complete API reference
- **[Player System](../architecture/player_system.md)**: Deep dive into player management

### 🎮 Try Advanced Features

- **Add AI Players**: Configure AI opponents
- **3-Player Mode**: Try the shared player mode
- **Custom Games**: Use player configurations

### 🛠️ Develop

- **[Contributing Guide](../CONTRIBUTING.md)**: Start contributing
- **[Development Guide](../guides/development_guide.md)**: Setup dev environment
- **[Testing Guide](../guides/testing_guide.md)**: Write tests

### 🧠 Train AI

- **[Training Guide](../training_guide.md)**: Train RL agents
- **RL Environment**: Explore the Gym environment

---

## Quick Reference

### Start Everything

```bash
# Terminal 1: API Server
cd blokus-server && python main.py

# Terminal 2: Frontend
cd blokus-web && python -m http.server 5500

# Terminal 3: Run tests
cd blokus-engine && pytest tests/ -v
```

### Useful Commands

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_game.py::TestGameInitialization::test_default_four_players

# Type checking
mypy src/blokus

# Linting
ruff check src/blokus

# Format code
ruff format src/blokus
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/game/new` | POST | Create game |
| `/game/state` | GET | Get state |
| `/game/move` | POST | Make move |
| `/game/pass` | POST | Pass turn |
| `/ai/models` | GET | List AI models |

---

## Congratulations! 🎉

You've successfully set up Blokus RL and played your first game!

**Questions?** Check the [documentation](../README.md) or open an issue on GitHub.

---

**Next**: [Adding AI Players →](adding_ai_player.md)
