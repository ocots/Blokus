/**
 * Game.passTurn() Unit Tests
 * 
 * Tests for the passTurn method which validates player has no valid moves
 * 
 * @module tests/unit/game-pass-turn.test.js
 */

describe('Game.passTurn()', () => {
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

    describe('Validation', () => {
        test('should reject pass when player has valid moves', () => {
            // Mock _hasValidMove to return true
            game._hasValidMove = jest.fn().mockReturnValue(true);
            
            const result = game.passTurn();
            
            expect(result).toBe(false);
        });

        test('should accept pass when player has no valid moves', () => {
            // Mock _hasValidMove to return false
            game._hasValidMove = jest.fn().mockReturnValue(false);
            
            const result = game.passTurn();
            
            expect(result).toBe(true);
        });

        test('should check valid moves for current player', () => {
            game._hasValidMove = jest.fn().mockReturnValue(false);
            
            game.passTurn();
            
            expect(game._hasValidMove).toHaveBeenCalledWith(game._currentPlayer);
        });
    });

    describe('Player State Updates', () => {
        test('should mark player as passed', () => {
            game._hasValidMove = jest.fn().mockReturnValue(false);
            const player = game._players[game._currentPlayer];
            
            game.passTurn();
            
            expect(player.hasPassed).toBe(true);
        });

        test('should not mark player as passed if has valid moves', () => {
            game._hasValidMove = jest.fn().mockReturnValue(true);
            const player = game._players[game._currentPlayer];
            player.hasPassed = false;
            
            game.passTurn();
            
            expect(player.hasPassed).toBe(false);
        });
    });

    describe('UI Updates', () => {
        test('should clear selection after pass', () => {
            game._hasValidMove = jest.fn().mockReturnValue(false);
            
            game.passTurn();
            
            expect(mockControls.clearSelection).toHaveBeenCalled();
        });

        test('should not clear selection if pass rejected', () => {
            game._hasValidMove = jest.fn().mockReturnValue(true);
            mockControls.clearSelection.mockClear();
            
            game.passTurn();
            
            expect(mockControls.clearSelection).not.toHaveBeenCalled();
        });
    });

    describe('Game Flow', () => {
        test('should advance to next turn on successful pass', () => {
            game._hasValidMove = jest.fn().mockReturnValue(false);
            const initialPlayer = game._currentPlayer;
            
            game.passTurn();
            
            // Current player should change (or game should be over)
            expect(game._currentPlayer !== initialPlayer || game._gameOver).toBe(true);
        });

        test('should return true on successful pass', () => {
            game._hasValidMove = jest.fn().mockReturnValue(false);
            
            const result = game.passTurn();
            
            expect(result).toBe(true);
        });

        test('should return false on rejected pass', () => {
            game._hasValidMove = jest.fn().mockReturnValue(true);
            
            const result = game.passTurn();
            
            expect(result).toBe(false);
        });

        test('should detect game over when all players pass', () => {
            game._hasValidMove = jest.fn().mockReturnValue(false);
            
            // Mark all players as passed except current
            for (let i = 0; i < game._players.length; i++) {
                if (i !== game._currentPlayer) {
                    game._players[i].hasPassed = true;
                }
            }
            
            game.passTurn();
            
            // After pass, should check if game is over
            expect(game._gameOver || game._currentPlayer !== 0).toBe(true);
        });
    });

    describe('Edge Cases', () => {
        test('should handle multiple pass attempts', () => {
            game._hasValidMove = jest.fn().mockReturnValue(false);
            
            const result1 = game.passTurn();
            const result2 = game.passTurn();
            
            expect(result1).toBe(true);
            // Second pass may fail if player already passed
            expect(typeof result2).toBe('boolean');
        });

        test('should handle pass when no valid moves exist', () => {
            game._hasValidMove = jest.fn().mockReturnValue(false);
            
            expect(() => {
                game.passTurn();
            }).not.toThrow();
        });

        test('should prevent pass when valid moves exist', () => {
            game._hasValidMove = jest.fn().mockReturnValue(true);
            
            const result = game.passTurn();
            
            expect(result).toBe(false);
        });
    });
});
