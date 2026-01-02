# AI System Refactoring Plan - SOLID Architecture

**Date**: 2026-01-02  
**Objective**: Refactor AI player system to follow SOLID principles and use state machines

---

## 🔍 Current Implementation Analysis

### Problems with Current Code

#### ❌ Violation SRP (Single Responsibility Principle)
`Game` class has too many responsibilities:
- Game state management
- Turn logic
- AI detection
- AI move scheduling
- AI move execution (local + API)
- Board management
- Score calculation

#### ❌ Violation OCP (Open/Closed Principle)
Adding new AI types requires modifying `Game` class:
```javascript
// Hard to extend without modifying
if (this._useApi) {
    await this._executeAIMoveFromAPI();
} else {
    await this._executeAIMoveLocal();
}
```

#### ❌ Violation DIP (Dependency Inversion Principle)
`Game` depends on concrete implementations:
- Direct calls to `_apiClient`
- Hard-coded AI logic in `_executeAIMoveLocal()`

#### ❌ No State Machine
Using boolean flags instead of explicit states:
- `_gameOver`
- Implicit AI "thinking" state
- No clear state transitions

---

## 🏗️ Proposed Architecture

### State Machines

#### 1. PlayerState Enum
```javascript
const PlayerState = {
    IDLE: 'idle',           // Waiting for turn
    ACTIVE: 'active',       // Human player's turn
    AI_THINKING: 'thinking', // AI is thinking
    AI_PLAYING: 'playing',  // AI is executing move
    PASSED: 'passed',       // Player has passed
    FINISHED: 'finished'    // Player finished (no pieces)
};
```

#### 2. GameState Enum
```javascript
const GameState = {
    SETUP: 'setup',
    PLAYING: 'playing',
    GAME_OVER: 'game_over'
};
```

#### 3. AIState Enum
```javascript
const AIState = {
    IDLE: 'idle',
    ANALYZING: 'analyzing',
    ANIMATING: 'animating',
    EXECUTING: 'executing',
    DONE: 'done'
};
```

---

## 📦 New Module Structure

### File Organization

```
blokus-web/js/
├── game.js              # Game orchestration only
├── board.js             # Board rendering
├── controls.js          # User input
├── api.js               # API client
├── ai/                  # NEW: AI module
│   ├── ai-controller.js # AI orchestration (SRP)
│   ├── ai-local.js      # Local AI implementation
│   ├── ai-api.js        # API AI implementation
│   └── ai-animator.js   # AI animations (Phase 2)
├── state/               # NEW: State management
│   ├── player-state.js  # Player state machine
│   └── game-state.js    # Game state machine
└── utils/
    └── state-machine.js # Generic state machine
```

---

## 🎯 Refactoring Steps

### Step 1: Create Generic State Machine

**File**: `blokus-web/js/utils/state-machine.js`

```javascript
/**
 * Generic State Machine
 * Follows OCP: extensible without modification
 */
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
            throw new Error(
                `Invalid transition: ${this._currentState} -> ${newState}`
            );
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

### Step 2: Create Player State Machine

**File**: `blokus-web/js/state/player-state.js`

```javascript
import { StateMachine } from '../utils/state-machine.js';

export const PlayerState = {
    IDLE: 'idle',
    ACTIVE: 'active',
    AI_THINKING: 'thinking',
    AI_PLAYING: 'playing',
    PASSED: 'passed',
    FINISHED: 'finished'
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

    activate() {
        this.transitionTo(PlayerState.ACTIVE);
    }

    startAIThinking() {
        this.transitionTo(PlayerState.AI_THINKING);
    }

    startAIPlaying() {
        this.transitionTo(PlayerState.AI_PLAYING);
    }

    pass() {
        this.transitionTo(PlayerState.PASSED);
    }

    finish() {
        this.transitionTo(PlayerState.FINISHED);
    }

    deactivate() {
        this.transitionTo(PlayerState.IDLE);
    }
}
```

### Step 3: Create AI Controller (SRP)

**File**: `blokus-web/js/ai/ai-controller.js`

```javascript
import { PlayerState } from '../state/player-state.js';

/**
 * AI Controller - Single Responsibility: Orchestrate AI moves
 * Follows DIP: Depends on AI strategy abstraction
 */
export class AIController {
    constructor(aiStrategy) {
        this._strategy = aiStrategy; // Dependency injection
        this._isThinking = false;
    }

    /**
     * Execute AI turn
     * @param {Object} gameContext - Game state and methods
     * @param {PlayerStateMachine} playerState - Player state machine
     */
    async executeTurn(gameContext, playerState) {
        if (this._isThinking) return;

        try {
            this._isThinking = true;
            playerState.startAIThinking();

            // Random delay 1-3s
            const delay = 1000 + Math.random() * 2000;
            await this._sleep(delay);

            playerState.startAIPlaying();

            // Get move from strategy
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
        } finally {
            this._isThinking = false;
        }
    }

    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
```

### Step 4: Create AI Strategies (OCP)

**File**: `blokus-web/js/ai/ai-local.js`

```javascript
/**
 * Local Random AI Strategy
 * Follows OCP: Can be extended/replaced without modifying AIController
 */
export class LocalAIStrategy {
    async getMove(gameContext) {
        const { playerId, players, board, isFirstMove, hasValidMove } = gameContext;

        if (!hasValidMove(playerId)) {
            return null; // No valid move
        }

        const player = players[playerId];
        const pieces = Array.from(player.remainingPieces);

        // Shuffle pieces
        this._shuffle(pieces);

        // Try each piece
        for (const type of pieces) {
            for (const piece of gameContext.getPieces(type)) {
                const corners = board.getPlayerCorners(playerId);
                this._shuffle(corners);

                for (const [cr, cc] of corners) {
                    for (const [pr, pc] of piece.coords) {
                        const row = cr - pr;
                        const col = cc - pc;

                        if (board.isValidPlacement(piece, row, col, playerId, isFirstMove(playerId))) {
                            return { piece, row, col };
                        }
                    }
                }
            }
        }

        return null; // No valid move found
    }

    _shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }
}
```

**File**: `blokus-web/js/ai/ai-api.js`

```javascript
/**
 * API AI Strategy
 * Follows DIP: Depends on API client abstraction
 */
export class APIAIStrategy {
    constructor(apiClient) {
        this._apiClient = apiClient;
    }

    async getMove(gameContext) {
        try {
            const response = await this._apiClient.getAISuggestedMove();

            if (response.success && response.move) {
                const { piece_type, orientation, row, col } = response.move;
                const piece = gameContext.getPiece(piece_type, orientation);
                return { piece, row, col };
            }

            return null;
        } catch (error) {
            console.error('API AI failed:', error);
            return null;
        }
    }
}
```

### Step 5: Refactor Game Class

**File**: `blokus-web/js/game.js` (simplified)

```javascript
import { AIController } from './ai/ai-controller.js';
import { LocalAIStrategy } from './ai/ai-local.js';
import { APIAIStrategy } from './ai/ai-api.js';
import { PlayerStateMachine, PlayerState } from './state/player-state.js';

export class Game {
    constructor(board, controls, config = {}, apiClient = null) {
        this._board = board;
        this._controls = controls;
        this._config = config;
        this._apiClient = apiClient;

        // Player state machines
        this._playerStates = [];
        
        // AI controllers (one per AI player)
        this._aiControllers = new Map();

        this._init();
    }

    _init() {
        // ... existing init code ...

        // Create state machines for each player
        for (let i = 0; i < this._numPlayers; i++) {
            const stateMachine = new PlayerStateMachine();
            this._playerStates.push(stateMachine);

            // Setup AI controller if player is AI
            if (this._isAIPlayer(i)) {
                const strategy = this._apiClient
                    ? new APIAIStrategy(this._apiClient)
                    : new LocalAIStrategy();
                
                this._aiControllers.set(i, new AIController(strategy));
            }
        }

        // Trigger first turn
        this._startTurn(this._currentPlayer);
    }

    _startTurn(playerId) {
        const playerState = this._playerStates[playerId];

        if (this._isAIPlayer(playerId)) {
            // AI player
            const aiController = this._aiControllers.get(playerId);
            const gameContext = this._createGameContext(playerId);
            
            aiController.executeTurn(gameContext, playerState);
        } else {
            // Human player
            playerState.activate();
        }

        this._updateUI();
    }

    _createGameContext(playerId) {
        return {
            playerId,
            players: this._players,
            board: this._board,
            isFirstMove: (pid) => this.isFirstMove(pid),
            hasValidMove: (pid) => this._hasValidMove(pid),
            getPieces: (type) => PIECES[type],
            getPiece: (type, orientation) => getPiece(type, orientation),
            playMove: (piece, row, col) => this.playMove(piece, row, col),
            passTurn: () => this.passTurn()
        };
    }

    _nextTurn() {
        // ... existing turn logic ...

        // Deactivate current player
        this._playerStates[this._currentPlayer].deactivate();

        // Find next player
        // ... existing code ...

        // Start next turn
        this._startTurn(this._currentPlayer);
    }

    _isAIPlayer(playerId) {
        return this._config.players?.[playerId]?.type === 'ai';
    }
}
```

---

## ✅ Benefits of Refactoring

### SOLID Compliance

1. **SRP**: Each class has one responsibility
   - `AIController`: Orchestrate AI turns
   - `LocalAIStrategy`: Generate moves locally
   - `APIAIStrategy`: Get moves from API
   - `PlayerStateMachine`: Manage player state
   - `Game`: Orchestrate game flow only

2. **OCP**: Easy to extend
   - Add new AI strategies without modifying `AIController`
   - Add new states without modifying `StateMachine`

3. **LSP**: Strategies are interchangeable
   - Any `AIStrategy` works with `AIController`

4. **ISP**: Focused interfaces
   - `gameContext` provides only what AI needs

5. **DIP**: Depend on abstractions
   - `AIController` depends on `AIStrategy` interface
   - `Game` injects dependencies

### Other Benefits

- **Testability**: Easy to mock strategies
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Add features without breaking existing code
- **Debuggability**: Clear state transitions
- **Type Safety**: Clear contracts (with JSDoc)

---

## 🧪 Testing Strategy

### Unit Tests

```javascript
// Test state machine
describe('PlayerStateMachine', () => {
    it('should allow valid transitions', () => {
        const sm = new PlayerStateMachine();
        expect(sm.state).toBe(PlayerState.IDLE);
        
        sm.activate();
        expect(sm.state).toBe(PlayerState.ACTIVE);
    });

    it('should reject invalid transitions', () => {
        const sm = new PlayerStateMachine();
        expect(() => sm.pass()).toThrow();
    });
});

// Test AI controller
describe('AIController', () => {
    it('should execute AI turn', async () => {
        const mockStrategy = { getMove: jest.fn().mockResolvedValue({ piece, row, col }) };
        const controller = new AIController(mockStrategy);
        
        await controller.executeTurn(gameContext, playerState);
        
        expect(mockStrategy.getMove).toHaveBeenCalled();
    });
});
```

---

## 📊 Migration Plan

### Phase 1: Create New Modules (No Breaking Changes)
1. Create `utils/state-machine.js`
2. Create `state/player-state.js`
3. Create `ai/ai-controller.js`
4. Create `ai/ai-local.js`
5. Create `ai/ai-api.js`

### Phase 2: Integrate with Game (Gradual)
1. Add state machines alongside existing flags
2. Add AI controllers alongside existing methods
3. Test both systems work in parallel

### Phase 3: Remove Old Code
1. Remove old AI methods from `Game`
2. Remove boolean flags
3. Clean up

### Phase 4: Add Animations
1. Create `ai/ai-animator.js`
2. Integrate with `AIController`

---

## 🎯 Success Criteria

- [ ] All SOLID principles respected
- [ ] State machines control all state transitions
- [ ] AI logic separated from Game class
- [ ] Easy to add new AI strategies
- [ ] Existing functionality preserved
- [ ] All tests passing
- [ ] Code coverage maintained

---

**Status**: Ready for implementation  
**Priority**: High (Technical debt + Feature enhancement)  
**Estimated Time**: 2-3 hours
