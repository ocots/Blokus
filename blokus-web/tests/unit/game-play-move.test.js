/**
 * Game.playMove() Unit Tests
 * 
 * Tests for the playMove method which is core game logic
 * 
 * @module tests/unit/game-play-move.test.js
 */

describe('Game.playMove()', () => {
    let game;
    let mockBoard;
    let mockControls;
    let mockConfig;

    beforeEach(() => {
        // Mock Board
        mockBoard = {
            init: jest.fn(),
            reset: jest.fn(),
            placePiece: jest.fn(),
            isValidPlacement: jest.fn().mockReturnValue(true),
            getPlayerCorners: jest.fn().mockReturnValue([[0, 0]]),
            render: jest.fn()
        };

        // Mock Controls
        mockControls = {
            setGame: jest.fn(),
            clearSelection: jest.fn(),
            selectPiece: jest.fn(),
            rotate: jest.fn(),
            flip: jest.fn()
        };

        // Mock Config
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

        // Create game instance
        game = new Game(mockBoard, mockControls, mockConfig, null);
    });

    describe('Basic Validation', () => {
        test('should reject invalid placement', () => {
            mockBoard.isValidPlacement.mockReturnValue(false);
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            
            const result = game.playMove(piece, 10, 10);
            
            expect(result).toBe(false);
            expect(mockBoard.placePiece).not.toHaveBeenCalled();
        });

        test('should accept valid placement', () => {
            mockBoard.isValidPlacement.mockReturnValue(true);
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            
            const result = game.playMove(piece, 10, 10);
            
            expect(result).toBe(true);
            expect(mockBoard.placePiece).toHaveBeenCalledWith(piece, 10, 10, 0);
        });

        test('should validate placement with correct player ID', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            game.playMove(piece, 10, 10);
            
            expect(mockBoard.isValidPlacement).toHaveBeenCalledWith(
                piece,
                10,
                10,
                game._currentPlayer,
                expect.any(Boolean)
            );
        });
    });

    describe('Player State Updates', () => {
        test('should remove piece from player remaining pieces', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            const player = game._players[0];
            const initialCount = player.remainingPieces.size;
            
            player.remainingPieces.add('I2');
            game.playMove(piece, 10, 10);
            
            expect(player.remainingPieces.has('I2')).toBe(false);
        });

        test('should track monomino placement', () => {
            const monomino = { type: 'I1', coords: [[0, 0]], orientationIndex: 0 };
            const player = game._players[0];
            
            game.playMove(monomino, 10, 10);
            
            expect(player.lastPieceWasMonomino).toBe(true);
        });

        test('should not mark non-monomino as monomino', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            const player = game._players[0];
            
            game.playMove(piece, 10, 10);
            
            expect(player.lastPieceWasMonomino).toBe(false);
        });
    });

    describe('Move History', () => {
        test('should record move in history', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            const initialCount = game._moveHistory.length;
            
            game.playMove(piece, 10, 10);
            
            expect(game._moveHistory.length).toBe(initialCount + 1);
        });

        test('should record correct move details', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            
            game.playMove(piece, 10, 10);
            
            const lastMove = game._moveHistory[game._moveHistory.length - 1];
            expect(lastMove.playerId).toBe(0);
            expect(lastMove.pieceType).toBe('I2');
            expect(lastMove.row).toBe(10);
            expect(lastMove.col).toBe(10);
        });
    });

    describe('UI Updates', () => {
        test('should clear selection after move', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            
            game.playMove(piece, 10, 10);
            
            expect(mockControls.clearSelection).toHaveBeenCalled();
        });

        test('should place piece on board', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            
            game.playMove(piece, 10, 10);
            
            expect(mockBoard.placePiece).toHaveBeenCalled();
        });
    });

    describe('Game Flow', () => {
        test('should advance to next turn', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            const initialPlayer = game._currentPlayer;
            
            game.playMove(piece, 10, 10);
            
            // Current player should change (or game should be over)
            expect(game._currentPlayer !== initialPlayer || game._gameOver).toBe(true);
        });

        test('should return true on success', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            
            const result = game.playMove(piece, 10, 10);
            
            expect(result).toBe(true);
        });

        test('should return false on failure', () => {
            mockBoard.isValidPlacement.mockReturnValue(false);
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            
            const result = game.playMove(piece, 10, 10);
            
            expect(result).toBe(false);
        });
    });

    describe('Edge Cases', () => {
        test('should handle null piece gracefully', () => {
            expect(() => {
                game.playMove(null, 10, 10);
            }).not.toThrow();
        });

        test('should handle undefined coordinates', () => {
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            
            expect(() => {
                game.playMove(piece, undefined, undefined);
            }).not.toThrow();
        });

        test('should handle negative coordinates', () => {
            mockBoard.isValidPlacement.mockReturnValue(false);
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            
            const result = game.playMove(piece, -5, -5);
            
            expect(result).toBe(false);
        });

        test('should handle out of bounds coordinates', () => {
            mockBoard.isValidPlacement.mockReturnValue(false);
            const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
            
            const result = game.playMove(piece, 100, 100);
            
            expect(result).toBe(false);
        });
    });
});
