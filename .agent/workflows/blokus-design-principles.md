---
description: Bonnes pratiques de design pour le projet Blokus RL (Python/JavaScript)
---

# Design Principles & Quality Objectives - Blokus RL

**Version**: 2.0  
**Last Updated**: 2026-01-02  
**Purpose**: Référence des principes de conception et objectifs qualité pour Python (backend/RL) et JavaScript (frontend)

**Updates v2.0**:
- Ajout section State Machines (machines à états)
- Architecture API client/serveur
- Patterns pour jeux de plateau avec menu
- Stratégies IA et injection de dépendances

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [SOLID Principles](#solid-principles)
3. [State Machines](#state-machines)
4. [API Architecture](#api-architecture)
5. [AI Strategy Pattern](#ai-strategy-pattern)
6. [Other Design Principles](#other-design-principles)
7. [Quality Objectives](#quality-objectives)
8. [Python-Specific Guidelines](#python-specific-guidelines)
9. [JavaScript-Specific Guidelines](#javascript-specific-guidelines)
10. [Quick Reference Checklists](#quick-reference-checklists)

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

## State Machines

### Why State Machines?

Pour un jeu de plateau avec menu, les **machines à états** sont essentielles :

- **Clarté** : États explicites vs flags booléens dispersés
- **Maintenabilité** : Transitions clairement définies
- **Debuggabilité** : Facile de tracer les changements d'état
- **Testabilité** : États et transitions facilement testables

### Generic State Machine Pattern

```javascript
// utils/state-machine.js
export class StateMachine {
    constructor(initialState, validTransitions) {
        this._currentState = initialState;
        this._validTransitions = validTransitions;
        this._listeners = [];
    }

    get state() {
        return this._currentState;
    }

    canTransitionTo(newState) {
        const allowed = this._validTransitions[this._currentState];
        return allowed && allowed.includes(newState);
    }

    transitionTo(newState) {
        if (!this.canTransitionTo(newState)) {
            throw new Error(`Invalid transition: ${this._currentState} -> ${newState}`);
        }
        const oldState = this._currentState;
        this._currentState = newState;
        this._notifyListeners(oldState, newState);
    }

    onTransition(callback) {
        this._listeners.push(callback);
    }

    _notifyListeners(oldState, newState) {
        this._listeners.forEach(cb => cb(oldState, newState));
    }
}
```

### Application State Machine

```javascript
// state/app-state.js
import { StateMachine } from '../utils/state-machine.js';

export const AppState = {
    INTRO: 'intro',       // Écran d'accueil
    SETUP: 'setup',       // Configuration de partie
    GAME: 'game',         // Partie en cours
    GAME_OVER: 'game_over' // Fin de partie
};

const APP_TRANSITIONS = {
    [AppState.INTRO]: [AppState.SETUP],
    [AppState.SETUP]: [AppState.GAME, AppState.INTRO],
    [AppState.GAME]: [AppState.GAME_OVER, AppState.SETUP],
    [AppState.GAME_OVER]: [AppState.SETUP, AppState.INTRO]
};

export class AppStateMachine extends StateMachine {
    constructor() {
        super(AppState.INTRO, APP_TRANSITIONS);
    }
}
```

### Player State Machine

```javascript
// state/player-state.js
export const PlayerState = {
    IDLE: 'idle',           // En attente
    ACTIVE: 'active',       // Tour du joueur humain
    AI_THINKING: 'thinking', // IA réfléchit
    AI_PLAYING: 'playing',  // IA joue
    PASSED: 'passed',       // A passé son tour
    FINISHED: 'finished'    // Terminé (plus de pièces)
};

const PLAYER_TRANSITIONS = {
    [PlayerState.IDLE]: [PlayerState.ACTIVE, PlayerState.AI_THINKING],
    [PlayerState.ACTIVE]: [PlayerState.IDLE, PlayerState.PASSED, PlayerState.FINISHED],
    [PlayerState.AI_THINKING]: [PlayerState.AI_PLAYING, PlayerState.PASSED],
    [PlayerState.AI_PLAYING]: [PlayerState.IDLE, PlayerState.FINISHED],
    [PlayerState.PASSED]: [PlayerState.FINISHED],
    [PlayerState.FINISHED]: []
};

export class PlayerStateMachine extends StateMachine {
    constructor() {
        super(PlayerState.IDLE, PLAYER_TRANSITIONS);
    }

    activate() { this.transitionTo(PlayerState.ACTIVE); }
    startAIThinking() { this.transitionTo(PlayerState.AI_THINKING); }
    startAIPlaying() { this.transitionTo(PlayerState.AI_PLAYING); }
    pass() { this.transitionTo(PlayerState.PASSED); }
    finish() { this.transitionTo(PlayerState.FINISHED); }
    deactivate() { this.transitionTo(PlayerState.IDLE); }
}
```

### Python State Machine (Backend)

```python
from enum import Enum
from typing import Dict, List, Callable

class GameStatus(Enum):
    SETUP = "setup"
    PLAYING = "playing"
    FINISHED = "finished"

class PlayerStatus(Enum):
    ACTIVE = "active"
    WAITING = "waiting"
    PASSED = "passed"
    FINISHED = "finished"

class StateMachine:
    def __init__(self, initial_state: Enum, transitions: Dict[Enum, List[Enum]]):
        self._state = initial_state
        self._transitions = transitions
        self._listeners: List[Callable] = []

    @property
    def state(self) -> Enum:
        return self._state

    def can_transition_to(self, new_state: Enum) -> bool:
        allowed = self._transitions.get(self._state, [])
        return new_state in allowed

    def transition_to(self, new_state: Enum) -> None:
        if not self.can_transition_to(new_state):
            raise ValueError(f"Invalid transition: {self._state} -> {new_state}")
        old_state = self._state
        self._state = new_state
        for listener in self._listeners:
            listener(old_state, new_state)

    def on_transition(self, callback: Callable) -> None:
        self._listeners.append(callback)
```

---

## API Architecture

### Client-Server Pattern

**Principe** : Séparation claire entre logique métier (backend) et présentation (frontend)

#### Backend (Python/FastAPI)

```python
# blokus-server/main.py
from fastapi import FastAPI, HTTPException
from blokus.game import Game
from blokus.game_manager_factory import GameManagerFactory

app = FastAPI()
game_instance: Optional[Game] = None

@app.post("/game/new")
def create_game(request: CreateGameRequest) -> GameState:
    """Create new game with player configurations"""
    global game_instance
    
    # Use factory for clean creation
    game_manager = GameManagerFactory.create_from_configs(
        player_configs=request.players,
        starting_player=request.start_player
    )
    
    game_instance = Game(
        num_players=request.num_players,
        game_manager=game_manager
    )
    
    return map_game_to_state(game_instance)

@app.post("/game/move")
def play_move(request: MoveRequest) -> MoveResponse:
    """Execute a move"""
    game = get_game_or_404()
    
    try:
        success = game.play_move(
            player_id=request.player_id,
            piece_type=request.piece_type,
            orientation=request.orientation,
            row=request.row,
            col=request.col
        )
        
        return MoveResponse(
            success=success,
            game_state=map_game_to_state(game)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/game/ai/suggest")
def get_ai_suggestion() -> AISuggestionResponse:
    """Get AI move suggestion for current player"""
    game = get_game_or_404()
    
    # Delegate to AI strategy
    current_player = game.players[game.current_player_idx]
    ai_strategy = get_ai_strategy(current_player.persona)
    
    move = ai_strategy.get_move(game)
    
    return AISuggestionResponse(
        success=move is not None,
        move=move
    )
```

#### Frontend (JavaScript)

```javascript
// api.js - API Client (SRP: Communication only)
export class APIClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this._baseUrl = baseUrl;
    }

    async createGame(numPlayers, startPlayer, players) {
        return this._request('/game/new', {
            method: 'POST',
            body: JSON.stringify({
                num_players: numPlayers,
                start_player: startPlayer,
                players: players
            })
        });
    }

    async playMove(playerId, pieceType, orientation, row, col) {
        return this._request('/game/move', {
            method: 'POST',
            body: JSON.stringify({
                player_id: playerId,
                piece_type: pieceType,
                orientation: orientation,
                row: row,
                col: col
            })
        });
    }

    async getAISuggestion() {
        return this._request('/game/ai/suggest', { method: 'POST' });
    }

    async _request(endpoint, options = {}) {
        const url = `${this._baseUrl}${endpoint}`;
        const response = await fetch(url, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }
        
        return await response.json();
    }
}
```

### Dual Mode Pattern

**Principe** : Support mode local ET mode API sans dupliquer la logique

```javascript
// game.js
export class Game {
    constructor(board, controls, config, apiClient = null) {
        this._board = board;
        this._controls = controls;
        this._config = config;
        this._apiClient = apiClient;
        this._useApi = apiClient !== null;
    }

    async playMove(piece, row, col) {
        if (this._useApi) {
            // Delegate to API
            const response = await this._apiClient.playMove(
                this._currentPlayer,
                piece.type,
                piece.orientationIndex,
                row,
                col
            );
            
            if (response.success) {
                this._syncFromServerState(response.game_state);
                return true;
            }
            return false;
        } else {
            // Local logic
            return this._playMoveLocal(piece, row, col);
        }
    }
}
```

---

## AI Strategy Pattern

### Why Strategy Pattern?

- **OCP** : Ajouter de nouvelles IA sans modifier le code existant
- **DIP** : Dépendre de l'abstraction `AIStrategy`, pas des implémentations
- **Testabilité** : Facile de mocker les stratégies

### AI Strategy Interface

```javascript
// ai/ai-strategy.js
/**
 * AI Strategy Interface (Protocol)
 * @interface
 */
export class AIStrategy {
    /**
     * Get next move for AI
     * @param {Object} gameContext - Game state and methods
     * @returns {Promise<{piece, row, col}|null>}
     */
    async getMove(gameContext) {
        throw new Error('getMove() must be implemented');
    }
}
```

### Concrete Strategies

```javascript
// ai/local-ai-strategy.js
import { AIStrategy } from './ai-strategy.js';

export class LocalAIStrategy extends AIStrategy {
    async getMove(gameContext) {
        // Random AI implementation
        const { playerId, players, board } = gameContext;
        
        // Find valid move
        for (const piece of this._shufflePieces(players[playerId])) {
            const move = this._findValidPlacement(piece, board, playerId);
            if (move) return move;
        }
        
        return null; // No valid move
    }
}

// ai/api-ai-strategy.js
export class APIAIStrategy extends AIStrategy {
    constructor(apiClient) {
        super();
        this._apiClient = apiClient;
    }

    async getMove(gameContext) {
        try {
            const response = await this._apiClient.getAISuggestion();
            return response.success ? response.move : null;
        } catch (error) {
            console.error('API AI failed:', error);
            return null;
        }
    }
}
```

### AI Controller (Orchestration)

```javascript
// ai/ai-controller.js (SRP: Orchestrate AI turns only)
export class AIController {
    constructor(aiStrategy) {
        this._strategy = aiStrategy; // Dependency injection
    }

    async executeTurn(gameContext, playerState) {
        try {
            playerState.startAIThinking();
            
            // Simulate thinking delay
            await this._sleep(1000 + Math.random() * 2000);
            
            playerState.startAIPlaying();
            
            // Get move from strategy (OCP: any strategy works)
            const move = await this._strategy.getMove(gameContext);
            
            if (move) {
                await gameContext.playMove(move.piece, move.row, move.col);
            } else {
                await gameContext.passTurn();
            }
            
            playerState.deactivate();
        } catch (error) {
            console.error('AI turn failed:', error);
            await gameContext.passTurn();
            playerState.deactivate();
        }
    }

    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
```

### Factory for AI Creation

```javascript
// ai/ai-factory.js (Factory Pattern)
import { LocalAIStrategy } from './local-ai-strategy.js';
import { APIAIStrategy } from './api-ai-strategy.js';
import { AIController } from './ai-controller.js';

export class AIFactory {
    static createController(useApi, apiClient = null) {
        const strategy = useApi
            ? new APIAIStrategy(apiClient)
            : new LocalAIStrategy();
        
        return new AIController(strategy);
    }
}
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
│   ├── pieces.py              # Définitions des 21 pièces
│   ├── board.py               # Logique du plateau 20x20
│   ├── rules.py               # Validation des règles Blokus
│   ├── game.py                # Orchestration de partie
│   ├── player.py              # Unified Player class
│   ├── player_types.py        # Enums (PlayerType, PlayerStatus, etc.)
│   ├── player_factory.py      # Factory for player creation
│   ├── game_manager.py        # Turn management
│   ├── game_manager_factory.py # Factory for GameManager
│   └── rl/
│       ├── environment.py     # Gym environment
│       └── registry.py        # AI model registry
└── tests/
    ├── test_pieces.py
    ├── test_board.py
    ├── test_game.py
    ├── test_player.py
    ├── test_player_factory.py
    ├── test_game_manager.py
    └── test_game_manager_factory.py

blokus-server/
├── main.py                    # FastAPI app
├── api/
│   └── models.py              # Pydantic models
└── tests/
    └── test_api_integration.py

blokus-web/
├── index.html
├── css/
│   └── style.css
└── js/
    ├── main.js                # Entry point
    ├── game.js                # Game orchestration
    ├── board.js               # Board rendering
    ├── controls.js            # User input
    ├── pieces.js              # Piece definitions
    ├── setup.js               # Setup menu
    ├── api.js                 # API client
    ├── state/                 # NEW: State machines
    │   ├── app-state.js
    │   └── player-state.js
    ├── ai/                    # NEW: AI module
    │   ├── ai-controller.js
    │   ├── ai-strategy.js
    │   ├── local-ai-strategy.js
    │   ├── api-ai-strategy.js
    │   ├── ai-factory.js
    │   └── ai-animator.js     # Animations
    └── utils/
        └── state-machine.js   # Generic state machine
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

### State Management with State Machines

```javascript
// State machines for each concern
import { AppStateMachine } from './state/app-state.js';
import { PlayerStateMachine } from './state/player-state.js';

class GameStateManager {
    constructor() {
        this._appState = new AppStateMachine();
        this._playerStates = [];
        
        // Listen to state transitions
        this._appState.onTransition((oldState, newState) => {
            console.log(`App: ${oldState} -> ${newState}`);
            this._updateUI(newState);
        });
    }

    initPlayers(numPlayers) {
        for (let i = 0; i < numPlayers; i++) {
            const playerState = new PlayerStateMachine();
            playerState.onTransition((old, now) => {
                console.log(`Player ${i}: ${old} -> ${now}`);
            });
            this._playerStates.push(playerState);
        }
    }

    startGame() {
        this._appState.transitionTo(AppState.GAME);
    }

    activatePlayer(playerId) {
        this._playerStates[playerId].activate();
    }
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
- [ ] Les machines à états sont définies pour la gestion d'état
- [ ] Les stratégies IA utilisent le pattern Strategy (OCP + DIP)
- [ ] L'API client est séparée de la logique métier (SRP)
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

**Architecture** :

- [ ] Machines à états pour tous les états complexes
- [ ] Pattern Strategy pour les IA (extensibilité)
- [ ] Factory Pattern pour la création d'objets
- [ ] Injection de dépendances (DIP)
- [ ] Séparation API client/serveur claire

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
