/**
 * AI System Tests
 * 
 * Tests for AI controller, strategies, and state machines
 * Covers bugs found during testing:
 * 1. Promise vs boolean return type mismatch
 * 2. Missing null checks on gameContext properties
 * 3. Invalid state transitions not caught early
 * 
 * @module tests/ai-system.test.js
 */

import { AIController } from '../js/ai/ai-controller.js';
import { LocalAIStrategy } from '../js/ai/local-ai-strategy.js';
import { APIAIStrategy } from '../js/ai/api-ai-strategy.js';
import { PlayerStateMachine, PlayerState } from '../js/state/player-state.js';
import { StateMachine } from '../js/utils/state-machine.js';

// ============================================================================
// TEST SUITE 1: Promise vs Boolean Return Type (BUG #1)
// ============================================================================

describe('AIController - Promise vs Boolean Handling', () => {
    let aiController;
    let mockStrategy;
    let mockPlayerState;
    let gameContextLocal;
    let gameContextAPI;

    beforeEach(() => {
        // Mock strategy
        mockStrategy = {
            getMove: async (context) => ({
                piece: { type: 'I2', coords: [[0, 0]], orientationIndex: 0 },
                row: 10,
                col: 10
            })
        };

        // Mock player state
        mockPlayerState = new PlayerStateMachine();

        // Local mode context (returns boolean)
        gameContextLocal = {
            playerId: 0,
            players: [{ remainingPieces: new Set(['I2']) }],
            board: {},
            isFirstMove: () => false,
            hasValidMove: () => true,
            getPieces: (type) => [{ type, coords: [[0, 0]], orientationIndex: 0 }],
            getPiece: (type, orientation) => ({ type, coords: [[0, 0]], orientationIndex: 0 }),
            playMove: (piece, row, col) => true, // Returns boolean
            passTurn: () => true
        };

        // API mode context (returns Promise)
        gameContextAPI = {
            playerId: 0,
            players: [{ remainingPieces: new Set(['I2']) }],
            board: {},
            isFirstMove: () => false,
            hasValidMove: () => true,
            getPieces: (type) => [{ type, coords: [[0, 0]], orientationIndex: 0 }],
            getPiece: (type, orientation) => ({ type, coords: [[0, 0]], orientationIndex: 0 }),
            playMove: (piece, row, col) => Promise.resolve(true), // Returns Promise
            passTurn: () => Promise.resolve(true)
        };

        aiController = new AIController(mockStrategy);
    });

    test('should handle boolean return from playMove (local mode)', async () => {
        await aiController.executeTurn(gameContextLocal, mockPlayerState);
        expect(mockPlayerState.state).toBe(PlayerState.IDLE);
    });

    test('should handle Promise return from playMove (API mode)', async () => {
        await aiController.executeTurn(gameContextAPI, mockPlayerState);
        expect(mockPlayerState.state).toBe(PlayerState.IDLE);
    });

    test('should handle boolean return from passTurn (local mode)', async () => {
        mockStrategy.getMove = async () => null; // No valid move
        await aiController.executeTurn(gameContextLocal, mockPlayerState);
        expect(mockPlayerState.state).toBe(PlayerState.IDLE);
    });

    test('should handle Promise return from passTurn (API mode)', async () => {
        mockStrategy.getMove = async () => null; // No valid move
        await aiController.executeTurn(gameContextAPI, mockPlayerState);
        expect(mockPlayerState.state).toBe(PlayerState.IDLE);
    });

    test('should not throw on mixed return types', async () => {
        // Mix of Promise and boolean
        const mixedContext = {
            ...gameContextLocal,
            playMove: (piece, row, col) => Promise.resolve(true)
        };

        expect(async () => {
            await aiController.executeTurn(mixedContext, mockPlayerState);
        }).not.toThrow();
    });
});

// ============================================================================
// TEST SUITE 2: Null/Undefined Checks (BUG #2)
// ============================================================================

describe('LocalAIStrategy - Null Safety', () => {
    let strategy;

    beforeEach(() => {
        strategy = new LocalAIStrategy();
    });

    test('should handle null gameContext gracefully', async () => {
        expect(async () => {
            await strategy.getMove(null);
        }).toThrow();
    });

    test('should handle missing hasValidMove function', async () => {
        const badContext = {
            playerId: 0,
            players: [{ remainingPieces: new Set() }],
            board: {},
            // Missing hasValidMove
            getPieces: () => []
        };

        expect(async () => {
            await strategy.getMove(badContext);
        }).toThrow();
    });

    test('should handle empty remainingPieces', async () => {
        const context = {
            playerId: 0,
            players: [{ remainingPieces: new Set() }],
            board: {},
            hasValidMove: () => false,
            getPieces: () => []
        };

        const move = await strategy.getMove(context);
        expect(move).toBeNull();
    });

    test('should handle null corners from board', async () => {
        const context = {
            playerId: 0,
            players: [{ remainingPieces: new Set(['I2']) }],
            board: {
                getPlayerCorners: () => null // Returns null
            },
            hasValidMove: () => true,
            getPieces: (type) => [{ type, coords: [[0, 0]] }]
        };

        const move = await strategy.getMove(context);
        expect(move).toBeNull();
    });

    test('should handle empty corners array', async () => {
        const context = {
            playerId: 0,
            players: [{ remainingPieces: new Set(['I2']) }],
            board: {
                getPlayerCorners: () => [] // Empty array
            },
            hasValidMove: () => true,
            getPieces: (type) => [{ type, coords: [[0, 0]] }]
        };

        const move = await strategy.getMove(context);
        expect(move).toBeNull();
    });
});

// ============================================================================
// TEST SUITE 3: State Machine Transitions (BUG #3)
// ============================================================================

describe('PlayerStateMachine - Valid Transitions', () => {
    let stateMachine;

    beforeEach(() => {
        stateMachine = new PlayerStateMachine();
    });

    test('should start in IDLE state', () => {
        expect(stateMachine.state).toBe(PlayerState.IDLE);
    });

    test('should allow IDLE -> ACTIVE transition', () => {
        expect(stateMachine.canTransitionTo(PlayerState.ACTIVE)).toBe(true);
        stateMachine.activate();
        expect(stateMachine.state).toBe(PlayerState.ACTIVE);
    });

    test('should allow IDLE -> AI_THINKING transition', () => {
        expect(stateMachine.canTransitionTo(PlayerState.AI_THINKING)).toBe(true);
        stateMachine.startAIThinking();
        expect(stateMachine.state).toBe(PlayerState.AI_THINKING);
    });

    test('should NOT allow ACTIVE -> AI_THINKING transition', () => {
        stateMachine.activate();
        expect(stateMachine.canTransitionTo(PlayerState.AI_THINKING)).toBe(false);
        expect(() => {
            stateMachine.startAIThinking();
        }).toThrow();
    });

    test('should NOT allow PASSED -> ACTIVE transition', () => {
        stateMachine.activate();
        stateMachine.pass();
        expect(stateMachine.canTransitionTo(PlayerState.ACTIVE)).toBe(false);
        expect(() => {
            stateMachine.activate();
        }).toThrow();
    });

    test('should allow AI_THINKING -> AI_PLAYING transition', () => {
        stateMachine.startAIThinking();
        expect(stateMachine.canTransitionTo(PlayerState.AI_PLAYING)).toBe(true);
        stateMachine.startAIPlaying();
        expect(stateMachine.state).toBe(PlayerState.AI_PLAYING);
    });

    test('should allow AI_THINKING -> PASSED transition', () => {
        stateMachine.startAIThinking();
        expect(stateMachine.canTransitionTo(PlayerState.PASSED)).toBe(true);
        stateMachine.pass();
        expect(stateMachine.state).toBe(PlayerState.PASSED);
    });

    test('should NOT allow FINISHED state to transition', () => {
        stateMachine.activate();
        stateMachine.finish();
        expect(stateMachine.canTransitionTo(PlayerState.IDLE)).toBe(false);
        expect(() => {
            stateMachine.deactivate();
        }).toThrow();
    });

    test('should track state transitions via listeners', () => {
        const transitions = [];
        stateMachine.onTransition((oldState, newState) => {
            transitions.push({ oldState, newState });
        });

        stateMachine.activate();
        stateMachine.pass();

        expect(transitions).toEqual([
            { oldState: PlayerState.IDLE, newState: PlayerState.ACTIVE },
            { oldState: PlayerState.ACTIVE, newState: PlayerState.PASSED }
        ]);
    });
});

// ============================================================================
// TEST SUITE 4: Generic StateMachine (BUG #3 - Foundation)
// ============================================================================

describe('StateMachine - Core Functionality', () => {
    let stateMachine;

    beforeEach(() => {
        const transitions = {
            'start': ['running', 'paused'],
            'running': ['paused', 'stopped'],
            'paused': ['running', 'stopped'],
            'stopped': []
        };
        stateMachine = new StateMachine('start', transitions);
    });

    test('should initialize with correct initial state', () => {
        expect(stateMachine.state).toBe('start');
    });

    test('should validate transitions before executing', () => {
        expect(stateMachine.canTransitionTo('running')).toBe(true);
        expect(stateMachine.canTransitionTo('stopped')).toBe(false);
    });

    test('should throw on invalid transition', () => {
        expect(() => {
            stateMachine.transitionTo('stopped');
        }).toThrow('Invalid transition: start -> stopped');
    });

    test('should execute valid transitions', () => {
        stateMachine.transitionTo('running');
        expect(stateMachine.state).toBe('running');

        stateMachine.transitionTo('paused');
        expect(stateMachine.state).toBe('paused');
    });

    test('should notify listeners on transition', () => {
        const listener = jest.fn();
        stateMachine.onTransition(listener);

        stateMachine.transitionTo('running');

        expect(listener).toHaveBeenCalledWith('start', 'running');
    });

    test('should support multiple listeners', () => {
        const listener1 = jest.fn();
        const listener2 = jest.fn();

        stateMachine.onTransition(listener1);
        stateMachine.onTransition(listener2);

        stateMachine.transitionTo('running');

        expect(listener1).toHaveBeenCalledWith('start', 'running');
        expect(listener2).toHaveBeenCalledWith('start', 'running');
    });
});

// ============================================================================
// TEST SUITE 5: APIAIStrategy - Error Handling (BUG #2)
// ============================================================================

describe('APIAIStrategy - Error Handling', () => {
    let strategy;
    let mockApiClient;

    beforeEach(() => {
        mockApiClient = {
            getAISuggestedMove: jest.fn()
        };
        strategy = new APIAIStrategy(mockApiClient);
    });

    test('should return null on API error', async () => {
        mockApiClient.getAISuggestedMove.mockRejectedValue(new Error('API Error'));

        const move = await strategy.getMove({});
        expect(move).toBeNull();
    });

    test('should return null when API returns no move', async () => {
        mockApiClient.getAISuggestedMove.mockResolvedValue({
            success: false,
            move: null
        });

        const move = await strategy.getMove({});
        expect(move).toBeNull();
    });

    test('should handle missing getPiece function gracefully', async () => {
        mockApiClient.getAISuggestedMove.mockResolvedValue({
            success: true,
            move: { piece_type: 'I2', orientation: 0, row: 10, col: 10 }
        });

        const context = {
            getPiece: undefined // Missing function
        };

        expect(async () => {
            await strategy.getMove(context);
        }).toThrow();
    });

    test('should return move when API succeeds', async () => {
        mockApiClient.getAISuggestedMove.mockResolvedValue({
            success: true,
            move: { piece_type: 'I2', orientation: 0, row: 10, col: 10 }
        });

        const context = {
            getPiece: (type, orientation) => ({
                type,
                coords: [[0, 0]],
                orientationIndex: orientation
            })
        };

        const move = await strategy.getMove(context);
        expect(move).not.toBeNull();
        expect(move.piece.type).toBe('I2');
        expect(move.row).toBe(10);
        expect(move.col).toBe(10);
    });
});
