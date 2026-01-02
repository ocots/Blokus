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

/**
 * AI Factory
 * Creates AI controllers with appropriate strategies
 */
export class AIFactory {
    /**
     * Create AI controller based on mode
     * @param {boolean} useApi - Whether to use API mode
     * @param {Object|null} apiClient - API client instance (required if useApi is true)
     * @returns {AIController}
     */
    static createController(useApi, apiClient = null) {
        const strategy = useApi
            ? new APIAIStrategy(apiClient)
            : new LocalAIStrategy();
        
        return new AIController(strategy);
    }

    /**
     * Create local AI controller
     * @returns {AIController}
     */
    static createLocalController() {
        return new AIController(new LocalAIStrategy());
    }

    /**
     * Create API AI controller
     * @param {Object} apiClient - API client instance
     * @returns {AIController}
     */
    static createAPIController(apiClient) {
        return new AIController(new APIAIStrategy(apiClient));
    }
}
