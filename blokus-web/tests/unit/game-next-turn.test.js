/**
 * Game._nextTurn() Unit Tests
 * 
 * Tests for the _nextTurn method which manages turn progression
 * 
 * @module tests/unit/game-next-turn.test.js
 */

describe('Game._nextTurn()', () => {
    let game;
    let mockBoard;
    let mockControls;
    let mockConfig;

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
    });

    describe('Player Deactivation', () => {
        test('should deactivate current player', () => {
            const playerState = game._playerStates[game._currentPlayer];
            playerState.activate = jest.fn();
            playerState.deactivate = jest.fn();
            
            game._nextTurn();
            
            expect(playerState.deactivate).toHaveBeenCalled();
        });

        test('should handle deactivate on non-existent player state', () => {
            game._playerStates[0] = null;
            
            expect(() => {
                game._nextTurn();
            }).not.toThrow();
        });
    });

    describe('Game Over Detection', () => {
        test('should detect game over when all players passed', () => {
            // Mark all players as passed
            for (let i = 0; i < game._players.length; i++) {
                game._players[i].hasPassed = true;
            }
            
            game._nextTurn();
            
            expect(game._gameOver).toBe(true);
        });

        test('should not end game when players can still play', () => {
            // Mark some players as passed, but not all
            game._players[0].hasPassed = true;
            game._players[1].hasPassed = true;
            // Players 2 and 3 can still play
            
            game._nextTurn();
            
            expect(game._gameOver).toBe(false);
        });

        test('should call _checkGameOver', () => {
            game._checkGameOver = jest.fn().mockReturnValue(false);
            
            game._nextTurn();
            
            expect(game._checkGameOver).toHaveBeenCalled();
        });
    });

    describe('Player Progression', () => {
        test('should advance to next player', () => {
            const initialPlayer = game._currentPlayer;
            
            game._nextTurn();
            
            // Should have moved to next player (or wrapped around)
            expect(game._currentPlayer).not.toBe(initialPlayer);
        });

        test('should skip passed players', () => {
            game._players[1].hasPassed = true;
            game._currentPlayer = 0;
            
            game._nextTurn();
            
            // Should skip player 1 and go to player 2 or beyond
            expect(game._currentPlayer).not.toBe(1);
        });

        test('should skip players with no remaining pieces', () => {
            game._players[1].remainingPieces.clear();
            game._currentPlayer = 0;
            
            game._nextTurn();
            
            // Should skip player 1 and mark them as passed
            expect(game._players[1].hasPassed).toBe(true);
        });

        test('should skip players with no valid moves', () => {
            game._hasValidMove = jest.fn((playerId) => playerId !== 1);
            game._currentPlayer = 0;
            
            game._nextTurn();
            
            // Should skip player 1 and mark them as passed
            expect(game._players[1].hasPassed).toBe(true);
        });

        test('should wrap around to first player', () => {
            game._currentPlayer = 3; // Last player
            game._players[0].hasPassed = false;
            
            game._nextTurn();
            
            // Should wrap to player 0
            expect(game._currentPlayer).toBe(0);
        });
    });

    describe('State Persistence', () => {
        test('should save game state', () => {
            game.save = jest.fn();
            
            game._nextTurn();
            
            expect(game.save).toHaveBeenCalled();
        });

        test('should call _startTurn for next player', () => {
            game._startTurn = jest.fn();
            
            game._nextTurn();
            
            expect(game._startTurn).toHaveBeenCalledWith(game._currentPlayer);
        });
    });

    describe('Edge Cases', () => {
        test('should handle all players passed', () => {
            for (let i = 0; i < game._players.length; i++) {
                game._players[i].hasPassed = true;
            }
            
            game._nextTurn();
            
            expect(game._gameOver).toBe(true);
        });

        test('should handle single player game', () => {
            game._numPlayers = 1;
            game._players = [game._players[0]];
            game._playerStates = [game._playerStates[0]];
            
            expect(() => {
                game._nextTurn();
            }).not.toThrow();
        });

        test('should handle rapid successive calls', () => {
            expect(() => {
                game._nextTurn();
                game._nextTurn();
                game._nextTurn();
            }).not.toThrow();
        });

        test('should handle player state machine errors gracefully', () => {
            game._playerStates[0].deactivate = jest.fn().mockImplementation(() => {
                throw new Error('State machine error');
            });
            
            expect(() => {
                game._nextTurn();
            }).not.toThrow();
        });
    });

    describe('Integration', () => {
        test('should complete full turn cycle', () => {
            const initialPlayer = game._currentPlayer;
            
            // Simulate a full cycle
            for (let i = 0; i < game._numPlayers; i++) {
                game._nextTurn();
            }
            
            // Should have cycled through all players
            expect(game._currentPlayer).not.toBe(initialPlayer);
        });

        test('should handle mixed passed and active players', () => {
            game._players[0].hasPassed = true;
            game._players[2].hasPassed = true;
            game._currentPlayer = 0;
            
            game._nextTurn();
            
            // Should find next active player
            expect(game._currentPlayer === 1 || game._currentPlayer === 3 || game._gameOver).toBe(true);
        });
    });
});
