/**
 * @jest-environment jsdom
 */

import { jest, describe, test, expect, beforeEach } from '@jest/globals';
import { AIController } from '../../js/ai/ai-controller.js';
import { PlayerStateMachine } from '../../js/state/player-state.js';

describe('AIController Error Recovery', () => {
    let aiController;
    let mockStrategy;
    let mockAnimator;
    let mockPlayerState;
    let gameContext;

    beforeEach(() => {
        mockStrategy = {
            getMove: jest.fn().mockResolvedValue(null)
        };

        mockAnimator = {
            showThinkingIndicator: jest.fn(),
            hideThinkingIndicator: jest.fn(),
            animateThinking: jest.fn().mockResolvedValue(undefined),
            animatePlacement: jest.fn().mockResolvedValue(undefined)
        };

        mockPlayerState = new PlayerStateMachine();

        gameContext = {
            playerId: 0,
            players: [{ remainingPieces: new Set(['I2']) }],
            board: {},
            isFirstMove: jest.fn().mockReturnValue(false),
            hasValidMove: jest.fn().mockReturnValue(true),
            getPieces: jest.fn().mockReturnValue([]),
            getPiece: jest.fn().mockReturnValue(null),
            playMove: jest.fn().mockReturnValue(true),
            passTurn: jest.fn().mockReturnValue(true)
        };

        aiController = new AIController(mockStrategy, mockAnimator);
    });

    describe('Animator Error Handling', () => {
        test('should handle animator error gracefully', async () => {
            mockAnimator.showThinkingIndicator.mockImplementation(() => {
                throw new Error('Animator error');
            });

            await expect(
                aiController.executeTurn(gameContext, mockPlayerState)
            ).resolves.not.toThrow();
        });

        test('should hide thinking indicator even on animator error', async () => {
            mockAnimator.animateThinking.mockRejectedValue(new Error('Animation failed'));

            await aiController.executeTurn(gameContext, mockPlayerState);

            expect(mockAnimator.hideThinkingIndicator).toHaveBeenCalled();
        });

        test('should continue to passTurn if animator fails', async () => {
            mockAnimator.animateThinking.mockRejectedValue(new Error('Animation failed'));
            mockStrategy.getMove.mockResolvedValue(null);

            await aiController.executeTurn(gameContext, mockPlayerState);

            expect(gameContext.passTurn).toHaveBeenCalled();
        });
    });

    describe('Strategy Error Handling', () => {
        test('should handle strategy error gracefully', async () => {
            mockStrategy.getMove.mockRejectedValue(new Error('Strategy failed'));

            await expect(
                aiController.executeTurn(gameContext, mockPlayerState)
            ).resolves.not.toThrow();
        });

        test('should call fallback passTurn on strategy error', async () => {
            mockStrategy.getMove.mockRejectedValue(new Error('Strategy failed'));

            await aiController.executeTurn(gameContext, mockPlayerState);

            expect(gameContext.passTurn).toHaveBeenCalled();
        });

        test('should deactivate player even on strategy error', async () => {
            mockStrategy.getMove.mockRejectedValue(new Error('Strategy failed'));
            mockPlayerState.deactivate = jest.fn();

            await aiController.executeTurn(gameContext, mockPlayerState);

            expect(mockPlayerState.deactivate).toHaveBeenCalled();
        });
    });

    describe('GameContext Error Handling', () => {
        test('should handle missing playMove method', async () => {
            const badContext = { ...gameContext, playMove: undefined };

            await expect(
                aiController.executeTurn(badContext, mockPlayerState)
            ).resolves.not.toThrow();
        });

        test('should handle missing passTurn method', async () => {
            const badContext = { ...gameContext, passTurn: undefined };

            await expect(
                aiController.executeTurn(badContext, mockPlayerState)
            ).resolves.not.toThrow();
        });

        test('should handle playMove throwing error', async () => {
            gameContext.playMove.mockImplementation(() => {
                throw new Error('PlayMove failed');
            });
            mockStrategy.getMove.mockResolvedValue({
                piece: { type: 'I2' },
                row: 10,
                col: 10
            });

            await expect(
                aiController.executeTurn(gameContext, mockPlayerState)
            ).resolves.not.toThrow();
        });

        test('should handle passTurn throwing error', async () => {
            gameContext.passTurn.mockImplementation(() => {
                throw new Error('PassTurn failed');
            });

            await expect(
                aiController.executeTurn(gameContext, mockPlayerState)
            ).resolves.not.toThrow();
        });
    });

    describe('State Machine Error Handling', () => {
        test('should handle state transition errors', async () => {
            mockPlayerState.startAIThinking = jest.fn().mockImplementation(() => {
                throw new Error('State transition failed');
            });

            await expect(
                aiController.executeTurn(gameContext, mockPlayerState)
            ).resolves.not.toThrow();
        });

        test('should deactivate player even on state error', async () => {
            mockPlayerState.startAIThinking = jest.fn().mockImplementation(() => {
                throw new Error('State transition failed');
            });
            mockPlayerState.deactivate = jest.fn();

            await aiController.executeTurn(gameContext, mockPlayerState);

            expect(mockPlayerState.deactivate).toHaveBeenCalled();
        });
    });

    describe('Concurrent Execution Prevention', () => {
        test('should prevent concurrent execution', async () => {
            mockStrategy.getMove.mockImplementation(
                () => new Promise(resolve => setTimeout(() => resolve(null), 100))
            );

            const promise1 = aiController.executeTurn(gameContext, mockPlayerState);
            const promise2 = aiController.executeTurn(gameContext, mockPlayerState);

            await Promise.all([promise1, promise2]);

            // Second call should have been prevented
            expect(mockStrategy.getMove).toHaveBeenCalledTimes(1);
        });

        test('should reset executing flag on error', async () => {
            mockStrategy.getMove.mockRejectedValue(new Error('Strategy failed'));

            await aiController.executeTurn(gameContext, mockPlayerState);

            // Should be able to execute again
            mockStrategy.getMove.mockResolvedValue(null);
            await aiController.executeTurn(gameContext, mockPlayerState);

            expect(mockStrategy.getMove).toHaveBeenCalledTimes(2);
        });
    });

    describe('Logging and Debugging', () => {
        test('should log errors for debugging', async () => {
            const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
            mockStrategy.getMove.mockRejectedValue(new Error('Strategy failed'));

            await aiController.executeTurn(gameContext, mockPlayerState);

            expect(consoleSpy).toHaveBeenCalled();
            consoleSpy.mockRestore();
        });

        test('should log error details', async () => {
            const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
            const testError = new Error('Test error message');
            mockStrategy.getMove.mockRejectedValue(testError);

            await aiController.executeTurn(gameContext, mockPlayerState);

            expect(consoleSpy).toHaveBeenCalledWith(expect.any(String), testError);
            consoleSpy.mockRestore();
        });
    });

    describe('Recovery Sequence', () => {
        test('should recover and allow next execution after error', async () => {
            // First execution with error
            mockStrategy.getMove.mockRejectedValueOnce(new Error('First error'));
            await aiController.executeTurn(gameContext, mockPlayerState);

            // Second execution should work
            mockStrategy.getMove.mockResolvedValueOnce(null);
            await aiController.executeTurn(gameContext, mockPlayerState);

            expect(mockStrategy.getMove).toHaveBeenCalledTimes(2);
        });

        test('should maintain state consistency after error recovery', async () => {
            mockStrategy.getMove.mockRejectedValue(new Error('Error'));

            await aiController.executeTurn(gameContext, mockPlayerState);

            // Player should be deactivated
            expect(mockPlayerState.state).not.toBe('thinking');
            expect(mockPlayerState.state).not.toBe('playing');
        });
    });

    describe('Edge Cases', () => {
        test('should handle null animator gracefully', async () => {
            const controllerNoAnimator = new AIController(mockStrategy, null);

            await expect(
                controllerNoAnimator.executeTurn(gameContext, mockPlayerState)
            ).resolves.not.toThrow();
        });

        test('should handle null strategy gracefully', async () => {
            const controllerNoStrategy = new AIController(null, mockAnimator);

            await expect(
                controllerNoStrategy.executeTurn(gameContext, mockPlayerState)
            ).resolves.not.toThrow();
        });

        test('should handle all errors simultaneously', async () => {
            mockAnimator.showThinkingIndicator.mockImplementation(() => {
                throw new Error('Animator error');
            });
            mockStrategy.getMove.mockRejectedValue(new Error('Strategy error'));
            gameContext.passTurn.mockImplementation(() => {
                throw new Error('PassTurn error');
            });

            await expect(
                aiController.executeTurn(gameContext, mockPlayerState)
            ).resolves.not.toThrow();
        });
    });
});
