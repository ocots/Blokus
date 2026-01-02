/**
 * AI Factory
 * 
 * Factory Pattern for creating AI controllers with appropriate strategies
 * Follows OCP: Easy to add new AI types without modifying this code
 * 
 * @module ai/ai-factory
 */

import { LocalAIStrategy } from './local-ai-strategy.js';
import { APIAIStrategy } from './api-ai-strategy.js';
import { AIController } from './ai-controller.js';
import { AIAnimator } from './ai-animator.js';

/**
 * AI Factory
 * Creates AI controllers with appropriate strategies
 */
export class AIFactory {
    /**
     * Create AI controller based on mode
     * @param {boolean} useApi - Whether to use API mode
     * @param {Object|null} apiClient - API client instance (required if useApi is true)
     * @param {Object|null} board - Board instance for animations
     * @param {Object|null} controls - Controls instance for animations
     * @returns {AIController}
     */
    static createController(useApi, apiClient = null, board = null, controls = null) {
        const strategy = useApi
            ? new APIAIStrategy(apiClient)
            : new LocalAIStrategy();
        
        // Create animator if board and controls are provided
        const animator = (board && controls) ? new AIAnimator(board, controls) : null;
        
        return new AIController(strategy, animator);
    }

    /**
     * Create local AI controller
     * @param {Object|null} board - Board instance for animations
     * @param {Object|null} controls - Controls instance for animations
     * @returns {AIController}
     */
    static createLocalController(board = null, controls = null) {
        const animator = (board && controls) ? new AIAnimator(board, controls) : null;
        return new AIController(new LocalAIStrategy(), animator);
    }

    /**
     * Create API AI controller
     * @param {Object} apiClient - API client instance
     * @param {Object|null} board - Board instance for animations
     * @param {Object|null} controls - Controls instance for animations
     * @returns {AIController}
     */
    static createAPIController(apiClient, board = null, controls = null) {
        const animator = (board && controls) ? new AIAnimator(board, controls) : null;
        return new AIController(new APIAIStrategy(apiClient), animator);
    }
}
