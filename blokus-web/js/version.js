/**
 * Version Configuration
 * 
 * Provides version tag for console logging to help identify
 * which version is running (useful for cache debugging)
 * 
 * @module version
 */

/**
 * Application version tag
 * Update this when deploying new versions to easily identify
 * which version is running in the console logs
 */
export const VERSION = {
    major: 1,
    minor: 0,
    patch: 0,
    tag: 'SOLID-REFACTOR-v1.0.0',
    buildDate: '2026-01-02',
    
    /**
     * Get full version string
     * @returns {string}
     */
    toString() {
        return `${this.tag} (${this.buildDate})`;
    },
    
    /**
     * Get console prefix for logging
     * @returns {string}
     */
    getLogPrefix() {
        return `[${this.tag}]`;
    }
};

/**
 * Log version info to console on startup
 */
export function logVersion() {
    console.log(`%c${VERSION.getLogPrefix()} Blokus App Started`, 'color: #00ff00; font-weight: bold; font-size: 12px;');
    console.log(`%cVersion: ${VERSION.toString()}`, 'color: #00ff00; font-size: 11px;');
}
