# Blokus RL

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-266%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-99.3%25-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **A complete Blokus board game implementation with AI agents trained via Reinforcement Learning**

Blokus RL is a professional-grade implementation of the strategic board game Blokus, featuring a high-performance Python game engine, modern web interface, and AI agents trained through reinforcement learning.

## ✨ Features

- 🎮 **Complete Game Implementation**: Full Blokus rules with 2 and 4 player support (including Blokus Duo and Standard modes)
- 🤖 **AI Players**: Multiple AI personas with adjustable speed (Fast Mode)
- 🧠 **Reinforcement Learning**: OpenAI Gym-compatible environment for training
- 🌐 **REST API**: FastAPI server with comprehensive endpoints
- 💻 **Modern Web UI**: Responsive interface with intuitive controls
- 💾 **Persistent Settings**: Player names, colors, and game preferences are automatically saved
- ⏪ **Replay System**: Review games with step-by-step controls and variable speed
- 🏗️ **SOLID Architecture**: Clean, maintainable, and extensible codebase
- ✅ **Fully Tested**: 266 tests with 99.3% coverage
- 📚 **Professional Documentation**: Complete guides and tutorials

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/ocots/Blokus.git
cd Blokus

# Setup backend
cd blokus-engine
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

### Start Playing

```bash
# Terminal 1: Start API server
cd blokus-server
python main.py

# Terminal 2: Start web interface
cd blokus-web
python -m http.server 5500

# Open http://localhost:5500 in your browser
```

**See [Quick Start Guide](docs/tutorials/quickstart.md) for detailed instructions.**

## 🏗️ Architecture

The project follows a modular, layered architecture:

```text
┌─────────────────────────────────────────────────────────┐
│                    Blokus RL System                      │
├─────────────────────────────────────────────────────────┤
│  Frontend (Web UI) ◄──► API Server ◄──► Game Engine    │
│  HTML/CSS/JS           FastAPI         Python           │
└─────────────────────────────────────────────────────────┘
```

### Modules

| Module | Description | Tech Stack |
|--------|-------------|------------|
| **blokus-server** | REST API server | FastAPI, Uvicorn |
| **blokus-web** | Web interface | HTML5, CSS3, JavaScript ES6+ |

**See [Architecture Overview](docs/architecture/overview.md) for details.**

## 📚 Documentation

### Getting Started
- 📖 [Quick Start Guide](docs/tutorials/quickstart.md) - Get up and running in 5 minutes
- 🏗️ [Architecture Overview](docs/architecture/overview.md) - System design and components
- 🎮 [Game Rules](docs/rules.md) - Complete Blokus rules

### Guides
- 🌐 [API Guide](docs/guides/api_guide.md) - Complete API reference with examples
- 💻 [Development Guide](docs/guides/development_guide.md) - Setup and development workflow
- 🧪 [Testing Guide](docs/guides/testing_guide.md) - Writing and running tests
- 🧠 [Training Guide](docs/training_guide.md) - Train RL agents

### Architecture
- 🎯 [Player System](docs/architecture/player_system.md) - Player and GameManager architecture
- 🎲 [Game Engine](docs/architecture/game_engine.md) - Core game logic
- 🔌 [API Design](docs/architecture/api_design.md) - REST API architecture

### Tutorials
- 🚀 [Quick Start](docs/tutorials/quickstart.md) - First steps
- 🤖 [Adding AI Players](docs/tutorials/adding_ai_player.md) - Create custom AI
- 🎨 [Frontend Customization](docs/tutorials/frontend_customization.md) - Customize the UI

## 🧪 Testing

```bash
# Run all tests
cd blokus-engine
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=blokus --cov-report=html

# Run specific test
pytest tests/test_game.py::TestGameInitialization -v

# Type checking
mypy src/blokus

# Linting
ruff check src/blokus
```

**Test Stats**: 266 tests passing | 99.3% coverage | 0 failures

## 🎮 Usage Examples

### Python API

```python
import requests

# Create a game
response = requests.post("http://localhost:8000/game/new", json={
    "num_players": 2,
    "players": [
        {"name": "Alice", "type": "human"},
        {"name": "Bot", "type": "ai", "persona": "random"}
    ]
})

# Make a move
response = requests.post("http://localhost:8000/game/move", json={
    "player_id": 0,
    "piece_type": "I5",
    "orientation": 0,
    "row": 0,
    "col": 0
})
```

### JavaScript

```javascript
// Create game
const response = await fetch('http://localhost:8000/game/new', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ num_players: 2 })
});
const gameState = await response.json();
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Commit (`git commit -m 'feat: add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📊 Project Status

- [Règles détaillées (2 & 4 joueurs)](docs/rules.md)
- [Guide d'entraînement d'IA](docs/training_guide.md)
- [Décisions de Design](docs/design_decisions.md)
- [Feuille de route (Roadmap)](docs/implementation_roadmap.md)

---
Développé avec ❤️ par l'équipe Blokus RL.
