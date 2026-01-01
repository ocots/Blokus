# Contributing to Blokus RL

Thank you for your interest in contributing to Blokus RL! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [Development Workflow](#development-workflow)
6. [Coding Standards](#coding-standards)
7. [Testing Guidelines](#testing-guidelines)
8. [Commit Guidelines](#commit-guidelines)
9. [Pull Request Process](#pull-request-process)
10. [Areas for Contribution](#areas-for-contribution)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Accept responsibility for mistakes

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing others' private information

---

## Getting Started

### Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 16+ (for frontend development)
- **Git**: For version control
- **IDE**: VS Code recommended (with Python and JavaScript extensions)

### Quick Start

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Blokus.git
cd Blokus

# 3. Add upstream remote
git remote add upstream https://github.com/ocots/Blokus.git

# 4. Create a branch
git checkout -b feature/your-feature-name

# 5. Make your changes and commit
git add .
git commit -m "feat: add your feature"

# 6. Push and create PR
git push origin feature/your-feature-name
```

---

## Development Setup

### Backend Setup (Python)

```bash
# Navigate to engine directory
cd blokus-engine

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

### Frontend Setup

```bash
# Navigate to web directory
cd blokus-web

# No build step required (vanilla JavaScript)
# Just open index.html in a browser or use Live Server
```

### API Server Setup

```bash
# Navigate to server directory
cd blokus-server

# Start the server
python main.py

# Server runs on http://localhost:8000
```

### Full Stack Development

```bash
# Terminal 1: Start API server
cd blokus-server
python main.py

# Terminal 2: Serve frontend
cd blokus-web
python -m http.server 5500
# Or use VS Code Live Server extension

# Access at http://localhost:5500
```

---

## Project Structure

```
Blokus/
├── blokus-engine/          # Core game engine (Python)
│   ├── src/blokus/         # Source code
│   │   ├── pieces.py       # Piece definitions
│   │   ├── board.py        # Board management
│   │   ├── rules.py        # Game rules
│   │   ├── game.py         # Game orchestration
│   │   ├── player.py       # Player system
│   │   ├── game_manager.py # Turn management
│   │   └── rl/             # RL environment
│   ├── tests/              # Test suite
│   └── pyproject.toml      # Python config
│
├── blokus-server/          # FastAPI server
│   ├── main.py             # API endpoints
│   ├── api/models.py       # Data models
│   └── tests/              # API tests
│
├── blokus-web/             # Frontend (HTML/CSS/JS)
│   ├── index.html          # Main page
│   ├── css/style.css       # Styling
│   └── js/                 # JavaScript modules
│       ├── main.js         # Entry point
│       ├── game.js         # Game logic
│       ├── board.js        # Rendering
│       ├── controls.js     # User input
│       └── api.js          # API client
│
└── docs/                   # Documentation
    ├── architecture/       # Architecture docs
    ├── guides/             # How-to guides
    └── tutorials/          # Step-by-step tutorials
```

---

## Development Workflow

### 1. Choose an Issue

- Browse [open issues](https://github.com/ocots/Blokus/issues)
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to claim it

### 2. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/issue-123-description

# Branch naming conventions:
# - feature/description  : New feature
# - fix/description      : Bug fix
# - docs/description     : Documentation
# - refactor/description : Code refactoring
# - test/description     : Test additions
```

### 3. Make Changes

- Write clean, well-documented code
- Follow coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run all tests
cd blokus-engine
pytest tests/ -v

# Run specific test file
pytest tests/test_game.py -v

# Run with coverage
pytest tests/ --cov=blokus --cov-report=html

# Type checking
mypy src/blokus

# Linting
ruff check src/blokus
```

### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add player turn management"

# See commit guidelines below
```

### 6. Push and Create PR

```bash
# Push to your fork
git push origin feature/issue-123-description

# Create Pull Request on GitHub
# Fill in the PR template
```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

```python
# Good: Clear, descriptive names
def calculate_valid_moves(board: Board, player: Player) -> List[Move]:
    """Calculate all valid moves for a player."""
    pass

# Bad: Unclear names
def calc(b, p):
    pass
```

#### Key Rules

1. **Line Length**: 100 characters (not 79)
2. **Indentation**: 4 spaces (no tabs)
3. **Naming**:
   - Classes: `PascalCase`
   - Functions/variables: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`
   - Private: `_leading_underscore`

4. **Type Hints**: Always use type hints

```python
def create_player(
    id: int,
    name: str,
    color: str,
    type: PlayerType = PlayerType.HUMAN
) -> Player:
    """Create a new player instance."""
    return Player(id=id, name=name, color=color, type=type)
```

5. **Docstrings**: Use Google style

```python
def play_move(self, move: Move) -> bool:
    """
    Execute a move on the board.
    
    Args:
        move: The move to execute
        
    Returns:
        True if move was successful, False otherwise
        
    Raises:
        ValueError: If move is invalid
    """
    pass
```

### JavaScript Style Guide

We follow **ES6+ standards**:

```javascript
// Good: Modern, clear
class GameManager {
    constructor(players) {
        this.players = players;
        this.currentPlayerIndex = 0;
    }
    
    nextTurn() {
        this.currentPlayerIndex = (this.currentPlayerIndex + 1) % this.players.length;
        return this.players[this.currentPlayerIndex];
    }
}

// Bad: Old style, unclear
var gm = function(p) {
    this.p = p;
    this.i = 0;
}
```

#### Key Rules

1. **Use `const` and `let`**: Never use `var`
2. **Arrow Functions**: Prefer arrow functions for callbacks
3. **Template Literals**: Use backticks for strings with variables
4. **Destructuring**: Use object/array destructuring
5. **Async/Await**: Prefer over `.then()` chains

```javascript
// Good
const { players, currentPlayer } = gameState;
const message = `Current player: ${currentPlayer.name}`;

// Bad
var players = gameState.players;
var message = 'Current player: ' + gameState.currentPlayer.name;
```

### SOLID Principles

All code must follow SOLID principles:

1. **Single Responsibility**: One class, one purpose
2. **Open/Closed**: Open for extension, closed for modification
3. **Liskov Substitution**: Subtypes must be substitutable
4. **Interface Segregation**: Small, focused interfaces
5. **Dependency Inversion**: Depend on abstractions

---

## Testing Guidelines

### Test Coverage Requirements

- **Core modules**: > 90% coverage required
- **Business logic**: > 85% coverage required
- **UI code**: > 70% coverage recommended

### Writing Good Tests

```python
import pytest
from blokus.player import Player
from blokus.player_types import PlayerType

class TestPlayer:
    """Test suite for Player class."""
    
    def test_create_human_player(self):
        """Test creating a human player."""
        player = Player(
            id=0,
            name="Alice",
            color="#3b82f6",
            type=PlayerType.HUMAN
        )
        
        assert player.id == 0
        assert player.name == "Alice"
        assert player.is_human
        assert not player.is_ai
    
    def test_play_piece_removes_from_remaining(self):
        """Test that playing a piece removes it from remaining pieces."""
        player = Player(id=0, name="Test", color="#000000")
        initial_count = player.pieces_count
        
        player.play_piece(PieceType.I1)
        
        assert player.pieces_count == initial_count - 1
        assert PieceType.I1 not in player.remaining_pieces
```

### Test Organization

```python
class TestClassName:
    """Test suite for ClassName."""
    
    # Group 1: Initialization tests
    def test_default_initialization(self):
        pass
    
    def test_custom_initialization(self):
        pass
    
    # Group 2: Method tests
    def test_method_success_case(self):
        pass
    
    def test_method_error_case(self):
        pass
    
    # Group 3: Edge cases
    def test_edge_case_empty_input(self):
        pass
    
    def test_edge_case_boundary(self):
        pass
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_player.py

# Run specific test
pytest tests/test_player.py::TestPlayer::test_create_human_player

# Run with coverage
pytest tests/ --cov=blokus --cov-report=html

# Run with verbose output
pytest tests/ -v

# Run only failed tests
pytest tests/ --lf
```

---

## Commit Guidelines

### Commit Message Format

We follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
# Good commits
git commit -m "feat(player): add unified Player class with GameManager"
git commit -m "fix(api): correct player state serialization"
git commit -m "docs(architecture): add player system documentation"
git commit -m "test(game): add tests for turn management"

# Bad commits
git commit -m "update stuff"
git commit -m "fix bug"
git commit -m "WIP"
```

### Commit Body (Optional)

```
feat(player): add unified Player class with GameManager

- Implement Player class with identity, state, and actions
- Create GameManager for centralized turn management
- Add PlayerFactory and GameManagerFactory
- 123 tests passing, follows SOLID principles

Closes #42
```

---

## Pull Request Process

### Before Submitting

- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Code Review**: Maintainer reviews code
3. **Feedback**: Address review comments
4. **Approval**: PR is approved
5. **Merge**: PR is merged to main

### After Merge

```bash
# Update your main branch
git checkout main
git pull upstream main

# Delete feature branch
git branch -d feature/issue-123-description
git push origin --delete feature/issue-123-description
```

---

## Areas for Contribution

### 🐛 Bug Fixes

Check [bug issues](https://github.com/ocots/Blokus/labels/bug) for reported bugs.

### ✨ New Features

- **AI Improvements**: Better RL agents, new personas
- **UI Enhancements**: Animations, themes, accessibility
- **Game Modes**: Tournament mode, time limits
- **Analytics**: Game statistics, replay system

### 📚 Documentation

- Improve existing docs
- Add code examples
- Create tutorials
- Translate documentation

### 🧪 Testing

- Increase test coverage
- Add integration tests
- Performance benchmarks
- Load testing

### 🎨 Design

- UI/UX improvements
- Accessibility enhancements
- Mobile responsiveness
- Theme customization

---

## Getting Help

### Resources

- **Documentation**: [docs/](../docs/)
- **Architecture**: [docs/architecture/](../docs/architecture/)
- **API Guide**: [docs/guides/api_guide.md](../docs/guides/api_guide.md)
- **Tutorials**: [docs/tutorials/](../docs/tutorials/)

### Communication

- **Issues**: [GitHub Issues](https://github.com/ocots/Blokus/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ocots/Blokus/discussions)
- **Email**: Contact maintainers directly

### Common Questions

**Q: How do I run the full application?**
```bash
# Terminal 1: API server
cd blokus-server && python main.py

# Terminal 2: Frontend
cd blokus-web && python -m http.server 5500
```

**Q: How do I add a new AI persona?**
See [tutorials/adding_ai_player.md](tutorials/adding_ai_player.md)

**Q: Tests are failing, what do I do?**
```bash
# Run tests with verbose output
pytest tests/ -v --tb=short

# Check specific failing test
pytest tests/test_file.py::test_name -v
```

---

## Recognition

Contributors will be:
- Listed in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Mentioned in release notes
- Credited in documentation

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](../LICENSE)).

---

## Thank You! 🎉

Your contributions make Blokus RL better for everyone. We appreciate your time and effort!

---

**Questions?** Open an issue or start a discussion on GitHub.
