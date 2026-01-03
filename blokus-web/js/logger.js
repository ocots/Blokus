
/**
 * Blokus Logger Module
 * Provides structured logging with levels and filtering.
 */

export const LogLevel = Object.freeze({
    DEBUG: 0,
    INFO: 1,
    API: 2,
    WARN: 3,
    ERROR: 4,
    NONE: 5
});

const LevelNames = ['DEBUG', 'INFO', 'API', 'WARN', 'ERROR', 'NONE'];

class Logger {
    constructor() {
        this.level = LogLevel.DEBUG; // Default level show all

        // Try load from local storage
        try {
            const saved = localStorage.getItem('blokus_log_level');
            if (saved !== null) {
                const parsed = parseInt(saved);
                if (!isNaN(parsed) && parsed >= 0 && parsed <= 5) {
                    this.level = parsed;
                }
            }
        } catch (e) {
            // Ignore (e.g. if localStorage is blocked)
        }
        console.log(`📝 Logger initialized at level: ${LevelNames[this.level]} (0=DEBUG, 1=INFO, 2=API, 3=WARN, 4=ERROR)`);
    }

    /**
     * Set logging level
     * @param {number} level - One of LogLevel constants
     */
    setLevel(level) {
        this.level = level;
        try {
            localStorage.setItem('blokus_log_level', level);
            console.log(`📝 Log Level set to ${LevelNames[level]}`);
        } catch (e) { }
    }

    /**
     * Get level from string name
     * @param {string} name 
     */
    getLevelByName(name) {
        const idx = LevelNames.indexOf(name.toUpperCase());
        return idx !== -1 ? idx : LogLevel.INFO;
    }

    debug(...args) {
        if (this.level <= LogLevel.DEBUG) {
            console.debug('%c🐛 [DEBUG]', 'color: #9ca3af', ...args);
        }
    }

    info(...args) {
        if (this.level <= LogLevel.INFO) {
            console.log('%cℹ️ [INFO]', 'color: #3b82f6', ...args);
        }
    }

    api(...args) {
        if (this.level <= LogLevel.API) {
            console.log('%c📡 [API]', 'color: #8b5cf6', ...args);
        }
    }

    warn(...args) {
        if (this.level <= LogLevel.WARN) {
            console.warn('%c⚠️ [WARN]', 'color: #f59e0b', ...args);
        }
    }

    error(...args) {
        if (this.level <= LogLevel.ERROR) {
            console.error('%c❌ [ERROR]', 'color: #ef4444', ...args);
        }
    }
}

export const logger = new Logger();
window.blokusLogger = logger; // Expose globally for console debugging
