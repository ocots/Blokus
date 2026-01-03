/**
 * AI Factory
 * 
 * Factory Pattern for creating AI controllers with appropriate strategies
 * 
 * @module ai/ai-factory
 */

import { LocalAIStrategy } from './local-ai-strategy.js';
import { APIAIStrategy } from './api-ai-strategy.js';
import { AIController } from './ai-controller.js';

/**
 * AI Factory
 * Creates AI controllers with appropriate strategies
 */
export class AIFactory {
    /**
     * Create AI controller based on mode
     * @param {boolean} useApi - Whether to use API mode
     * @param {Object|null} apiClient - API client instance
     * @param {Object} options - Optional configuration (e.g. fastMode)
     * @returns {AIController}
     */
    static createController(useApi, apiClient, options = {}) {
        const strategy = useApi
            ? new APIAIStrategy(apiClient)
            : new LocalAIStrategy();
        
        return new AIController(strategy, options);
    }

    /**
     * Create local AI controller
     * @param {Object} options - Optional configuration
     * @returns {AIController}
     */
    static createLocalController(options = {}) {
        return new AIController(new LocalAIStrategy(), options);
    }

    /**
     * Create API AI controller
     * @param {Object} apiClient - API client instance
     * @param {Object} options - Optional configuration
     * @returns {AIController}
     */
    static createAPIController(apiClient, options = {}) {
        return new AIController(new APIAIStrategy(apiClient), options);
    }
}
