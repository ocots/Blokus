/**
 * AIAnimator Unit Tests
 * 
 * Tests for AI animation system
 * Covers the bug where setSelectedPiece() was called instead of selectPiece()
 * 
 * @module tests/unit/ai-animator.test.js
 */

import { AIAnimator } from '../../js/ai/ai-animator.js';

describe('AIAnimator', () => {
    let animator;
    let mockBoard;
    let mockControls;
    let mockPiece;

    beforeEach(() => {
        // Mock Board
        mockBoard = {
            showPreview: jest.fn(),
            clearPreview: jest.fn(),
            render: jest.fn()
        };

        // Mock Controls
        mockControls = {
            selectPiece: jest.fn(),
            clearSelection: jest.fn()
        };

        // Mock Piece
        mockPiece = {
            type: 'I2',
            coords: [[0, 0], [1, 0]],
            orientationIndex: 0
        };

        animator = new AIAnimator(mockBoard, mockControls);
    });

    describe('animateThinking', () => {
        test('should call selectPiece with piece type', async () => {
            await animator.animateThinking(mockPiece, 10, 10, 100);
            expect(mockControls.selectPiece).toHaveBeenCalledWith(mockPiece.type);
        });

        test('should call showPreview with piece and position', async () => {
            await animator.animateThinking(mockPiece, 10, 10, 100);
            expect(mockBoard.showPreview).toHaveBeenCalledWith(mockPiece, 10, 10);
        });

        test('should call clearPreview after duration', async () => {
            await animator.animateThinking(mockPiece, 10, 10, 50);
            expect(mockBoard.clearPreview).not.toHaveBeenCalled();
            
            await new Promise(resolve => setTimeout(resolve, 100));
            expect(mockBoard.clearPreview).toHaveBeenCalled();
        });

        test('should call clearSelection after duration', async () => {
            await animator.animateThinking(mockPiece, 10, 10, 50);
            
            await new Promise(resolve => setTimeout(resolve, 100));
            expect(mockControls.clearSelection).toHaveBeenCalled();
        });

        test('should handle null piece gracefully', async () => {
            await animator.animateThinking(null, 10, 10, 100);
            expect(mockControls.selectPiece).not.toHaveBeenCalled();
        });

        test('should handle undefined row gracefully', async () => {
            await animator.animateThinking(mockPiece, undefined, 10, 100);
            expect(mockBoard.showPreview).not.toHaveBeenCalled();
        });

        test('should handle undefined col gracefully', async () => {
            await animator.animateThinking(mockPiece, 10, undefined, 100);
            expect(mockBoard.showPreview).not.toHaveBeenCalled();
        });

        test('should return a Promise', () => {
            const result = animator.animateThinking(mockPiece, 10, 10, 100);
            expect(result instanceof Promise).toBe(true);
        });
    });

    describe('animatePlacement', () => {
        test('should call board render', async () => {
            await animator.animatePlacement(mockPiece, 10, 10);
            expect(mockBoard.render).toHaveBeenCalled();
        });

        test('should handle null piece gracefully', async () => {
            await animator.animatePlacement(null, 10, 10);
            expect(mockBoard.render).not.toHaveBeenCalled();
        });

        test('should return a Promise', () => {
            const result = animator.animatePlacement(mockPiece, 10, 10);
            expect(result instanceof Promise).toBe(true);
        });
    });

    describe('showThinkingIndicator', () => {
        test('should create DOM element with correct ID', () => {
            animator.showThinkingIndicator(0);
            const indicator = document.getElementById('ai-thinking-0');
            expect(indicator).not.toBeNull();
        });

        test('should create element with correct class', () => {
            animator.showThinkingIndicator(0);
            const indicator = document.getElementById('ai-thinking-0');
            expect(indicator.classList.contains('ai-thinking-indicator')).toBe(true);
        });

        test('should create element with thinking text', () => {
            animator.showThinkingIndicator(0);
            const indicator = document.getElementById('ai-thinking-0');
            expect(indicator.textContent).toContain('Réflexion');
        });

        test('should handle different player IDs', () => {
            animator.showThinkingIndicator(1);
            animator.showThinkingIndicator(2);
            animator.showThinkingIndicator(3);
            
            expect(document.getElementById('ai-thinking-1')).not.toBeNull();
            expect(document.getElementById('ai-thinking-2')).not.toBeNull();
            expect(document.getElementById('ai-thinking-3')).not.toBeNull();
        });
    });

    describe('hideThinkingIndicator', () => {
        test('should remove DOM element', () => {
            animator.showThinkingIndicator(0);
            expect(document.getElementById('ai-thinking-0')).not.toBeNull();
            
            animator.hideThinkingIndicator(0);
            expect(document.getElementById('ai-thinking-0')).toBeNull();
        });

        test('should handle non-existent element gracefully', () => {
            expect(() => {
                animator.hideThinkingIndicator(999);
            }).not.toThrow();
        });

        test('should handle multiple hide calls', () => {
            animator.showThinkingIndicator(0);
            animator.hideThinkingIndicator(0);
            expect(() => {
                animator.hideThinkingIndicator(0);
            }).not.toThrow();
        });
    });

    describe('Integration', () => {
        test('should handle complete animation sequence', async () => {
            animator.showThinkingIndicator(0);
            await animator.animateThinking(mockPiece, 10, 10, 50);
            await animator.animatePlacement(mockPiece, 10, 10);
            animator.hideThinkingIndicator(0);
            
            expect(mockControls.selectPiece).toHaveBeenCalled();
            expect(mockBoard.showPreview).toHaveBeenCalled();
            expect(mockBoard.clearPreview).toHaveBeenCalled();
            expect(mockControls.clearSelection).toHaveBeenCalled();
            expect(mockBoard.render).toHaveBeenCalled();
            expect(document.getElementById('ai-thinking-0')).toBeNull();
        });

        test('should handle multiple animations without interference', async () => {
            const piece1 = { type: 'I2', coords: [[0, 0]] };
            const piece2 = { type: 'T4', coords: [[0, 0]] };
            
            await Promise.all([
                animator.animateThinking(piece1, 10, 10, 50),
                animator.animateThinking(piece2, 15, 15, 50)
            ]);
            
            expect(mockControls.selectPiece).toHaveBeenCalledWith('I2');
            expect(mockControls.selectPiece).toHaveBeenCalledWith('T4');
        });
    });

    afterEach(() => {
        // Clean up DOM
        document.querySelectorAll('.ai-thinking-indicator').forEach(el => el.remove());
    });
});
