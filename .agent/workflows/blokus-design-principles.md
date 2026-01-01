---
description: Bonnes pratiques de design pour le projet Blokus RL (Python/JavaScript)
---

# Design Principles & Quality Objectives - Blokus RL

**Version**: 1.0  
**Last Updated**: 2026-01-01  
**Purpose**: Référence des principes de conception et objectifs qualité pour Python (backend/RL) et JavaScript (frontend)

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [SOLID Principles](#solid-principles)
3. [Other Design Principles](#other-design-principles)
4. [Quality Objectives](#quality-objectives)
5. [Python-Specific Guidelines](#python-specific-guidelines)
6. [JavaScript-Specific Guidelines](#javascript-specific-guidelines)
7. [Quick Reference Checklists](#quick-reference-checklists)

---

## Introduction

Ce document adapte les principes SOLID et autres bonnes pratiques pour notre projet Blokus RL, combinant Python (moteur de jeu, RL) et JavaScript (interface web).

**Philosophie clé** : Un bon design n'est pas de suivre des règles aveuglément, mais de comprendre les compromis et prendre des décisions éclairées.

---

## SOLID Principles

### S - Single Responsibility Principle (SRP)

**Définition** : Chaque module, fonction et classe doit avoir une seule responsabilité bien définie.

**Python Examples**:

✅ **Good** - Séparation claire :

```python
# pieces.py - Uniquement les définitions de pièces
class Piece:
    def __init__(self, shape: np.ndarray):
        self.shape = shape
    
    def rotate(self) -> 'Piece':
        return Piece(np.rot90(self.shape))

# rules.py - Uniquement la validation
def is_valid_placement(board: Board, piece: Piece, pos: tuple) -> bool:
    return _has_corner_contact(board, piece, pos) and \
           not _has_edge_contact(board, piece, pos)

# game.py - Orchestration uniquement
class BlokusGame:
    def play_move(self, player_id: int, piece: Piece, pos: tuple):
        if not is_valid_placement(self.board, piece, pos):
            raise InvalidMoveError()
        self.board.place(piece, pos)
```

❌ **Bad** - Trop de responsabilités :

```python
class BlokusGame:
    def play_and_validate_and_render(self, move):
        # Validation
        if not self._check_rules(move):
            raise Error()
        # Placement
        self.board[move.pos] = move.piece
        # Rendu (!)
        self._draw_board()
        # Sauvegarde (!)
        self._save_to_file()
```

**JavaScript Examples**:

✅ **Good** :

```javascript
// board.js - Rendu uniquement
function renderBoard(ctx, gameState) { ... }

// controls.js - Inputs uniquement
function handlePieceRotation(event) { ... }

// api.js - Communication serveur uniquement
async function fetchAISuggestion(state) { ... }
```

---

### O - Open/Closed Principle (OCP)

**Définition** : Ouvert à l'extension, fermé à la modification.

**Python Examples**:

✅ **Good** - Extensible via héritage/duck typing :

```python
from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def select_action(self, state: GameState) -> Action:
        pass

class RandomAgent(Agent):
    def select_action(self, state: GameState) -> Action:
        return random.choice(state.valid_actions)

class DQNAgent(Agent):
    def select_action(self, state: GameState) -> Action:
        q_values = self.network(state.tensor)
        return self._epsilon_greedy(q_values)

# Nouveau type sans modifier le code existant
class MCTSAgent(Agent):
    def select_action(self, state: GameState) -> Action:
        return self.mcts_search(state)
```

❌ **Bad** - Modification requise pour extension :

```python
def get_action(agent_type: str, state):
    if agent_type == "random":
        return random.choice(state.valid_actions)
    elif agent_type == "dqn":
        return dqn_select(state)
    # Besoin d'ajouter ici pour chaque nouveau type!
```

---

### L - Liskov Substitution Principle (LSP)

**Définition** : Les sous-types doivent respecter le contrat du type parent.

**Python Examples**:

✅ **Good** - Interface cohérente :

```python
class Environment(ABC):
    @abstractmethod
    def step(self, action) -> tuple[State, float, bool, dict]:
        """Returns (next_state, reward, done, info)"""
        pass

class BlokusEnv2P(Environment):
    def step(self, action) -> tuple[State, float, bool, dict]:
        # Respecte le contrat de retour
        return next_state, reward, done, {}

class BlokusEnv4P(Environment):
    def step(self, action) -> tuple[State, float, bool, dict]:
        # Même signature, même comportement attendu
        return next_state, reward, done, {}
```

---

### I - Interface Segregation Principle (ISP)

**Définition** : Ne pas forcer l'implémentation d'interfaces inutilisées.

**Python Examples**:

✅ **Good** - Interfaces minimales :

```python
from typing import Protocol

class Evaluable(Protocol):
    def evaluate(self, state: State) -> float: ...

class Trainable(Protocol):
    def train(self, batch: list) -> float: ...

# DQN implémente les deux
class DQNAgent:
    def evaluate(self, state): return self.q_network(state).max()
    def train(self, batch): return self._update(batch)

# Random n'implémente que Evaluable (via duck typing)
class RandomAgent:
    def evaluate(self, state): return 0.0  # No real evaluation
```

---

### D - Dependency Inversion Principle (DIP)

**Définition** : Dépendre des abstractions, pas des implémentations concrètes.

**Python Examples**:

✅ **Good** - Injection de dépendances :

```python
class Trainer:
    def __init__(self, env: Environment, agent: Agent, logger: Logger):
        self.env = env      # Abstraction
        self.agent = agent  # Abstraction
        self.logger = logger

# Facile à tester avec des mocks
trainer = Trainer(
    env=MockEnvironment(),
    agent=RandomAgent(),
    logger=FileLogger("train.log")
)
```

❌ **Bad** - Dépendances concrètes :

```python
class Trainer:
    def __init__(self):
        self.env = BlokusEnv4P()  # Couplage fort
        self.agent = DQNAgent()   # Impossible de substituer
        self.logger = print       # Pas de flexibilité
```

---

## Other Design Principles

### DRY - Don't Repeat Yourself

**Python** :

```python
# Extraire la logique commune
def validate_position(pos: tuple[int, int], board_size: int = 20) -> bool:
    return 0 <= pos[0] < board_size and 0 <= pos[1] < board_size

# Utiliser partout
if validate_position(pos):
    ...
```

**JavaScript** :

```javascript
// utils.js
export function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}
```

### KISS - Keep It Simple, Stupid

Préférer les solutions simples. Éviter la sur-ingénierie.

### YAGNI - You Aren't Gonna Need It

N'implémenter que ce qui est nécessaire maintenant. Pas de code "au cas où".

### POLA - Principle of Least Astonishment

Noms clairs, comportements prévisibles :

- Python : `get_*` pour lecture, `set_*` pour écriture, `is_*` pour booléens
- JavaScript : `handle*` pour event handlers, `render*` pour rendu

### POLP - Principle of Least Privilege

Exposer le minimum nécessaire :

- Python : `__all__` pour contrôler les exports, `_prefix` pour le privé
- JavaScript : `export` explicites, fonctions internes sans export

---

## Quality Objectives

### 1. Reusability (Réutilisabilité)

- Composants modulaires et indépendants
- Interfaces claires et documentées
- Couplage minimal

### 2. Performance

**Python (RL)** :

- Utiliser `numpy` pour les opérations matricielles
- Vectoriser les opérations sur les batches
- Profiler : `cProfile`, `line_profiler`

**JavaScript** :

- Minimiser les reflows/repaints
- Utiliser `requestAnimationFrame` pour les animations
- Éviter les closures dans les boucles critiques

### 3. Maintainability (Maintenabilité)

- Code auto-documenté avec noms explicites
- Docstrings Python, JSDoc JavaScript
- Fonctions < 50 lignes
- Pas de code mort

### 4. Safety (Sécurité)

- Validation des entrées
- Gestion explicite des erreurs
- Types : `typing` Python, TypeScript optionnel pour JS

---

## Python-Specific Guidelines

### Type Hints

```python
from typing import Optional, List, Tuple
from dataclasses import dataclass

@dataclass
class Move:
    piece_id: int
    position: Tuple[int, int]
    orientation: int

def get_valid_moves(state: GameState) -> List[Move]:
    ...
```

### Project Structure

```
blokus-engine/
├── src/blokus/
│   ├── __init__.py
│   ├── pieces.py      # Définitions des 21 pièces
│   ├── board.py       # Logique du plateau 20x20
│   ├── rules.py       # Validation des règles Blokus
│   ├── game.py        # Orchestration de partie
│   └── player.py      # Gestion des joueurs
└── tests/
    └── test_*.py
```

### Testing

```bash
# Tests avec couverture
pytest tests/ -v --cov=src/blokus --cov-report=term-missing

# Type checking
mypy src/

# Linting
ruff check src/
```

---

## JavaScript-Specific Guidelines

### Modules ES6

```javascript
// board.js
export function renderBoard(ctx, state) { ... }
export function highlightValidMoves(ctx, moves) { ... }

// Imports explicites
import { renderBoard, highlightValidMoves } from './board.js';
```

### State Management

```javascript
// État centralisé
const gameState = {
    board: new Array(20).fill(null).map(() => new Array(20).fill(0)),
    currentPlayer: 0,
    remainingPieces: { 0: [...], 1: [...], 2: [...], 3: [...] },
    selectedPiece: null,
    aiEnabled: false
};

// Mutations via fonctions dédiées
function placePiece(state, playerId, piece, position) {
    // Modifier l'état de manière contrôlée
}
```

### Event Handling

```javascript
// Séparation handler / logique
function handleBoardClick(event) {
    const pos = screenToBoard(event.clientX, event.clientY);
    if (isValidPosition(pos)) {
        attemptPlacement(pos);
    }
}
```

---

## Quick Reference Checklists

### Avant de coder

- [ ] La responsabilité de chaque module est claire (SRP)
- [ ] Le design permet l'extension sans modification (OCP)
- [ ] Les interfaces sont définies (types Python, JSDoc JS)
- [ ] Les tests sont planifiés

### Code Review

**SOLID** :

- [ ] Fonctions/modules ont une seule responsabilité
- [ ] Code extensible sans modification
- [ ] Sous-types respectent les contrats parents
- [ ] Interfaces non surchargées
- [ ] Dépendances via abstractions

**Autres principes** :

- [ ] Pas de duplication (DRY)
- [ ] Solution la plus simple (KISS)
- [ ] Pas de code spéculatif (YAGNI)
- [ ] Comportement prévisible (POLA)
- [ ] Exports minimaux (POLP)

### Testing

- [ ] Tests unitaires pour chaque module public
- [ ] Tests d'intégration pour les workflows complets
- [ ] Couverture > 80%
- [ ] Tests des cas limites et erreurs

---

## References

- **Python** : [PEP 8](https://peps.python.org/pep-0008/), [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- **JavaScript** : [MDN Best Practices](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Best_practices)
- **SOLID** : [Wikipedia](https://en.wikipedia.org/wiki/SOLID)

---

**Note** : Ce document est vivant et sera mis à jour au fur et à mesure de l'évolution du projet.
