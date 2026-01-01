# Blokus RL Documentation

**Complete documentation for the Blokus RL project**

---

## 📚 Documentation Structure

### 🚀 Getting Started

| Document | Description |
|----------|-------------|
| [Quick Start Guide](tutorials/quickstart.md) | Get up and running in 5 minutes |
| [Contributing Guide](CONTRIBUTING.md) | How to contribute to the project |

### 🏗️ Architecture

| Document | Description |
|----------|-------------|
| [Architecture Overview](architecture/overview.md) | Complete system architecture |
| [Player System](architecture/player_system.md) | Player & GameManager architecture |
| Game Engine | Core game logic (coming soon) |
| API Design | REST API architecture (coming soon) |

### 📖 Guides

| Document | Description |
|----------|-------------|
| [API Guide](guides/api_guide.md) | Complete API reference with examples |
| Development Guide | Setup and workflow (coming soon) |
| Testing Guide | Writing and running tests (coming soon) |
| [Training Guide](training_guide.md) | Train RL agents |

### 🎓 Tutorials

| Document | Description |
|----------|-------------|
| [Quick Start](tutorials/quickstart.md) | First steps with Blokus RL |
| Adding AI Players | Create custom AI (coming soon) |
| Frontend Customization | Customize the UI (coming soon) |

### 📋 Reference

| Document | Description |
|----------|-------------|
| [Game Rules](rules.md) | Complete Blokus rules |
| [Design Decisions](design_decisions.md) | Technical choices and rationale |
| [Implementation Roadmap](implementation_roadmap.md) | Development phases |
| [Modeling Analysis](modeling_analysis.md) | RL modeling approaches |
| [UI Design](ui_design.md) | Interface specifications |

---

## 🗂️ Project Structure

```
Blokus/
├── docs/                      # 📚 Documentation (this directory)
│   ├── architecture/          # System architecture docs
│   ├── guides/                # How-to guides
│   ├── tutorials/             # Step-by-step tutorials
│   ├── CONTRIBUTING.md        # Contribution guide
│   └── README.md              # This file
│
├── blokus-engine/             # 🎮 Python game engine
│   ├── src/blokus/            # Source code
│   │   ├── player.py          # Unified Player class
│   │   ├── game_manager.py    # Turn management
│   │   ├── game.py            # Game orchestration
│   │   └── rl/                # RL environment
│   └── tests/                 # Test suite (266 tests)
│
├── blokus-server/             # 🌐 FastAPI server
│   ├── main.py                # API endpoints
│   └── api/models.py          # Data models
│
├── blokus-web/                # 💻 Web interface
│   ├── index.html             # Main page
│   ├── css/style.css          # Styling
│   └── js/                    # JavaScript modules
│
└── .agent/workflows/          # 🔧 Development workflows
```

---

## 📊 Documentation Stats

- **Total Documents**: 15+
- **Architecture Docs**: 2 (more coming)
- **Guides**: 4
- **Tutorials**: 1 (more coming)
- **Reference Docs**: 5
- **Code Examples**: 50+
- **Diagrams**: 10+

---

## 🔍 Quick Links

### For Users
- [Quick Start](tutorials/quickstart.md) - Start here!
- [Game Rules](rules.md) - Learn how to play
- [API Guide](guides/api_guide.md) - Use the API

### For Developers
- [Contributing](CONTRIBUTING.md) - Join the project
- [Architecture](architecture/overview.md) - Understand the system
- [Player System](architecture/player_system.md) - Core architecture

### For Researchers
- [Training Guide](training_guide.md) - Train AI agents
- [Modeling Analysis](modeling_analysis.md) - RL approaches
- [Design Decisions](design_decisions.md) - Technical choices

---

## 🆕 Recent Updates

**2026-01-01**: Major documentation overhaul
- ✅ Added comprehensive architecture documentation
- ✅ Created professional contributing guide
- ✅ Added complete API reference
- ✅ Created quick start tutorial
- ✅ Documented Player/GameManager architecture

---

## 🤝 Contributing to Documentation

Found an error or want to improve the docs? See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Documentation Standards

- **Markdown**: All docs in Markdown format
- **Structure**: Clear headings and sections
- **Examples**: Include code examples
- **Links**: Cross-reference related docs
- **Diagrams**: Use ASCII art or Mermaid

---

## 📞 Need Help?

- **Issues**: [GitHub Issues](https://github.com/ocots/Blokus/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ocots/Blokus/discussions)

---

**Last Updated**: 2026-01-01  
**Documentation Version**: 2.0
