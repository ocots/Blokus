/**
 * PlayerStateMachine Edge Cases Unit Tests
 * 
 * Tests for state machine edge cases and idempotency
 * Covers the race condition bug where deactivate() was called multiple times
 * 
 * @module tests/unit/player-state-machine.test.js
 */

import { PlayerStateMachine, PlayerState } from '../../js/state/player-state.js';

describe('PlayerStateMachine Edge Cases', () => {
    let stateMachine;

    beforeEach(() => {
        stateMachine = new PlayerStateMachine();
    });

    describe('Deactivate Idempotency', () => {
        test('should be safe to call deactivate multiple times', () => {
            stateMachine.activate();
            
            expect(() => {
                stateMachine.deactivate();
                stateMachine.deactivate();
                stateMachine.deactivate();
            }).not.toThrow();
        });

        test('should remain in IDLE after multiple deactivate calls', () => {
            stateMachine.activate();
            stateMachine.deactivate();
            stateMachine.deactivate();
            stateMachine.deactivate();
            
            expect(stateMachine.state).toBe(PlayerState.IDLE);
        });

        test('should handle deactivate from IDLE state', () => {
            expect(stateMachine.state).toBe(PlayerState.IDLE);
            
            expect(() => {
                stateMachine.deactivate();
            }).not.toThrow();
            
            expect(stateMachine.state).toBe(PlayerState.IDLE);
        });

        test('should handle deactivate from FINISHED state', () => {
            stateMachine.activate();
            stateMachine.finish();
            
            expect(() => {
                stateMachine.deactivate();
            }).not.toThrow();
            
            expect(stateMachine.state).toBe(PlayerState.FINISHED);
        });

        test('should handle deactivate from AI_PLAYING state', () => {
            stateMachine.startAIThinking();
            stateMachine.startAIPlaying();
            
            expect(() => {
                stateMachine.deactivate();
            }).not.toThrow();
            
            expect(stateMachine.state).toBe(PlayerState.IDLE);
        });

        test('should handle rapid successive deactivate calls', () => {
            stateMachine.activate();
            
            for (let i = 0; i < 10; i++) {
                expect(() => {
                    stateMachine.deactivate();
                }).not.toThrow();
            }
            
            expect(stateMachine.state).toBe(PlayerState.IDLE);
        });
    });

    describe('Multiple Rapid Transitions', () => {
        test('should handle rapid state changes', () => {
            expect(() => {
                stateMachine.activate();
                stateMachine.deactivate();
                stateMachine.activate();
                stateMachine.deactivate();
            }).not.toThrow();
        });

        test('should handle AI thinking to playing to idle', () => {
            expect(() => {
                stateMachine.startAIThinking();
                stateMachine.startAIPlaying();
                stateMachine.deactivate();
            }).not.toThrow();
            
            expect(stateMachine.state).toBe(PlayerState.IDLE);
        });

        test('should handle complex transition sequence', () => {
            expect(() => {
                stateMachine.activate();
                stateMachine.deactivate();
                stateMachine.startAIThinking();
                stateMachine.startAIPlaying();
                stateMachine.deactivate();
                stateMachine.activate();
                stateMachine.deactivate();
            }).not.toThrow();
        });
    });

    describe('Transition Listeners', () => {
        test('should call listeners on valid transitions', () => {
            const listener = jest.fn();
            stateMachine.onTransition(listener);
            
            stateMachine.activate();
            
            expect(listener).toHaveBeenCalledWith(PlayerState.IDLE, PlayerState.ACTIVE);
        });

        test('should not call listeners on invalid transitions', () => {
            const listener = jest.fn();
            stateMachine.onTransition(listener);
            
            stateMachine.activate();
            listener.mockClear();
            
            // Try invalid transition
            expect(() => {
                stateMachine.startAIThinking();
            }).toThrow();
            
            expect(listener).not.toHaveBeenCalled();
        });

        test('should call multiple listeners', () => {
            const listener1 = jest.fn();
            const listener2 = jest.fn();
            const listener3 = jest.fn();
            
            stateMachine.onTransition(listener1);
            stateMachine.onTransition(listener2);
            stateMachine.onTransition(listener3);
            
            stateMachine.activate();
            
            expect(listener1).toHaveBeenCalled();
            expect(listener2).toHaveBeenCalled();
            expect(listener3).toHaveBeenCalled();
        });

        test('should call listeners for each transition', () => {
            const listener = jest.fn();
            stateMachine.onTransition(listener);
            
            stateMachine.activate();
            stateMachine.deactivate();
            stateMachine.activate();
            
            expect(listener).toHaveBeenCalledTimes(3);
        });
    });

    describe('State Consistency', () => {
        test('should maintain consistent state after errors', () => {
            stateMachine.activate();
            
            // Try invalid transition
            try {
                stateMachine.startAIThinking();
            } catch (e) {
                // Expected to throw
            }
            
            // State should still be ACTIVE
            expect(stateMachine.state).toBe(PlayerState.ACTIVE);
        });

        test('should recover from invalid transition attempts', () => {
            stateMachine.activate();
            
            try {
                stateMachine.startAIThinking();
            } catch (e) {
                // Expected
            }
            
            // Should still be able to deactivate
            expect(() => {
                stateMachine.deactivate();
            }).not.toThrow();
            
            expect(stateMachine.state).toBe(PlayerState.IDLE);
        });

        test('should maintain state after listener errors', () => {
            const listener = jest.fn().mockImplementation(() => {
                throw new Error('Listener error');
            });
            stateMachine.onTransition(listener);
            
            // Transition should still work even if listener throws
            try {
                stateMachine.activate();
            } catch (e) {
                // May throw due to listener error
            }
            
            // State should have transitioned
            expect(stateMachine.state).toBe(PlayerState.ACTIVE);
        });
    });

    describe('Helper Methods', () => {
        test('isActive should return true only for ACTIVE state', () => {
            expect(stateMachine.isActive()).toBe(false);
            
            stateMachine.activate();
            expect(stateMachine.isActive()).toBe(true);
            
            stateMachine.deactivate();
            expect(stateMachine.isActive()).toBe(false);
        });

        test('isAIActive should return true for AI states', () => {
            expect(stateMachine.isAIActive()).toBe(false);
            
            stateMachine.startAIThinking();
            expect(stateMachine.isAIActive()).toBe(true);
            
            stateMachine.startAIPlaying();
            expect(stateMachine.isAIActive()).toBe(true);
            
            stateMachine.deactivate();
            expect(stateMachine.isAIActive()).toBe(false);
        });

        test('isDone should return true for PASSED and FINISHED', () => {
            expect(stateMachine.isDone()).toBe(false);
            
            stateMachine.activate();
            stateMachine.pass();
            expect(stateMachine.isDone()).toBe(true);
            
            stateMachine.deactivate();
            stateMachine.finish();
            expect(stateMachine.isDone()).toBe(true);
        });
    });

    describe('Concurrent Operations', () => {
        test('should handle concurrent activate/deactivate safely', async () => {
            const promises = [];
            
            for (let i = 0; i < 5; i++) {
                promises.push(
                    Promise.resolve().then(() => {
                        try {
                            stateMachine.activate();
                        } catch (e) {
                            // May fail due to invalid transition
                        }
                    })
                );
                
                promises.push(
                    Promise.resolve().then(() => {
                        try {
                            stateMachine.deactivate();
                        } catch (e) {
                            // May fail due to invalid transition
                        }
                    })
                );
            }
            
            await Promise.all(promises);
            
            // Should end in a valid state
            expect([PlayerState.IDLE, PlayerState.ACTIVE].includes(stateMachine.state)).toBe(true);
        });
    });
});
