/**
 * GameContext Dependency Injection Unit Tests
 * 
 * Tests for GameContext object passed to AI strategies
 * Ensures all required methods exist and are callable
 * 
 * @module tests/unit/game-context.test.js
 */

describe('GameContext Dependency Injection', () => {
    let game;
    let mockBoard;
    let mockControls;
    let mockConfig;
    let gameContext;

    beforeEach(() => {
        mockBoard = {
            init: jest.fn(),
            reset: jest.fn(),
            placePiece: jest.fn(),
            isValidPlacement: jest.fn().mockReturnValue(true),
            getPlayerCorners: jest.fn().mockReturnValue([[0, 0]]),
            render: jest.fn()
        };

        mockControls = {
            setGame: jest.fn(),
            clearSelection: jest.fn(),
            selectPiece: jest.fn()
        };

        mockConfig = {
            playerCount: 4,
            players: [
                { name: 'Player 1', type: 'human' },
                { name: 'AI 1', type: 'ai', persona: 'random' },
                { name: 'AI 2', type: 'ai', persona: 'random' },
                { name: 'AI 3', type: 'ai', persona: 'random' }
            ],
            startPlayer: 0,
            twoPlayerMode: null
        };

        game = new Game(mockBoard, mockControls, mockConfig, null);
        gameContext = game._createGameContext(0);
    });

    describe('Required Properties', () => {
        test('should have playerId property', () => {
            expect(gameContext.playerId).toBeDefined();
            expect(typeof gameContext.playerId).toBe('number');
        });

        test('should have players property', () => {
            expect(gameContext.players).toBeDefined();
            expect(Array.isArray(gameContext.players)).toBe(true);
        });

        test('should have board property', () => {
            expect(gameContext.board).toBeDefined();
            expect(gameContext.board).toBe(mockBoard);
        });
    });

    describe('Required Methods', () => {
        test('should have isFirstMove method', () => {
            expect(typeof gameContext.isFirstMove).toBe('function');
        });

        test('should have hasValidMove method', () => {
            expect(typeof gameContext.hasValidMove).toBe('function');
        });

        test('should have getPieces method', () => {
            expect(typeof gameContext.getPieces).toBe('function');
        });

        test('should have getPiece method', () => {
            expect(typeof gameContext.getPiece).toBe('function');
        });

        test('should have playMove method', () => {
            expect(typeof gameContext.playMove).toBe('function');
        });

        test('should have passTurn method', () => {
            expect(typeof gameContext.passTurn).toBe('function');
        });
    });

    describe('Method Functionality', () => {
        test('isFirstMove should be callable', () => {
            expect(() => {
                gameContext.isFirstMove(0);
            }).not.toThrow();
        });

        test('hasValidMove should be callable', () => {
            expect(() => {
                gameContext.hasValidMove(0);
            }).not.toThrow();
        });

        test('getPieces should return array', () => {
            const pieces = gameContext.getPieces('I2');
            expect(Array.isArray(pieces) || pieces === undefined).toBe(true);
        });

        test('getPiece should be callable', () => {
            expect(() => {
                gameContext.getPiece('I2', 0);
            }).not.toThrow();
        });

        test('playMove should be callable', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            expect(() => {
                gameContext.playMove(piece, 10, 10);
            }).not.toThrow();
        });

        test('passTurn should be callable', () => {
            expect(() => {
                gameContext.passTurn();
            }).not.toThrow();
        });
    });

    describe('Context Isolation', () => {
        test('should create independent contexts for different players', () => {
            const context0 = game._createGameContext(0);
            const context1 = game._createGameContext(1);
            
            expect(context0.playerId).toBe(0);
            expect(context1.playerId).toBe(1);
        });

        test('should share same board reference', () => {
            const context0 = game._createGameContext(0);
            const context1 = game._createGameContext(1);
            
            expect(context0.board).toBe(context1.board);
        });

        test('should share same players reference', () => {
            const context0 = game._createGameContext(0);
            const context1 = game._createGameContext(1);
            
            expect(context0.players).toBe(context1.players);
        });
    });

    describe('Error Handling', () => {
        test('should handle invalid player ID gracefully', () => {
            expect(() => {
                game._createGameContext(999);
            }).not.toThrow();
        });

        test('should handle null player ID gracefully', () => {
            expect(() => {
                game._createGameContext(null);
            }).not.toThrow();
        });

        test('should handle undefined player ID gracefully', () => {
            expect(() => {
                game._createGameContext(undefined);
            }).not.toThrow();
        });
    });

    describe('Method Return Types', () => {
        test('isFirstMove should return boolean', () => {
            const result = gameContext.isFirstMove(0);
            expect(typeof result).toBe('boolean');
        });

        test('hasValidMove should return boolean', () => {
            const result = gameContext.hasValidMove(0);
            expect(typeof result).toBe('boolean');
        });

        test('playMove should return boolean or Promise', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            const result = gameContext.playMove(piece, 10, 10);
            expect(typeof result === 'boolean' || result instanceof Promise).toBe(true);
        });

        test('passTurn should return boolean or Promise', () => {
            const result = gameContext.passTurn();
            expect(typeof result === 'boolean' || result instanceof Promise).toBe(true);
        });
    });

    describe('Integration', () => {
        test('should allow AI strategy to use all methods', () => {
            expect(() => {
                // Simulate AI strategy usage
                if (gameContext.hasValidMove(gameContext.playerId)) {
                    const pieces = gameContext.getPieces('I2');
                    if (pieces && pieces.length > 0) {
                        const piece = gameContext.getPiece('I2', 0);
                        gameContext.playMove(piece, 10, 10);
                    }
                } else {
                    gameContext.passTurn();
                }
            }).not.toThrow();
        });

        test('should maintain consistency across method calls', () => {
            const playerId1 = gameContext.playerId;
            const playerId2 = gameContext.playerId;
            
            expect(playerId1).toBe(playerId2);
        });
    });
});
