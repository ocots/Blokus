/**
 * LocalStorageObserver (Observer)
 * Persists SettingsStore state to localStorage.
 * Features: Debouncing, Versioning, Error Handling.
 */
export class LocalStorageObserver {
    static STORAGE_KEY = 'blokus_settings';
    static STORAGE_VERSION = '1.0';
    static DEBOUNCE_MS = 300;

    constructor() {
        this.timeoutId = null;
    }

    /**
     * Called when SettingsStore updates.
     * Debounces the save operation.
     */
    update(state) {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }

        this.timeoutId = setTimeout(() => {
            this._save(state);
        }, LocalStorageObserver.DEBOUNCE_MS);
    }

    /**
     * Internal save method.
     */
    _save(state) {
        try {
            const payload = {
                version: LocalStorageObserver.STORAGE_VERSION,
                timestamp: Date.now(),
                data: state
            };
            localStorage.setItem(LocalStorageObserver.STORAGE_KEY, JSON.stringify(payload));
            // debug log (optional)
            // console.log('Settings saved to localStorage', state);
        } catch (e) {
            console.error('Failed to save settings to localStorage:', e);
            // Handle QuotaExceededError or Private Mode access denied
        }
    }

    /**
     * Load state from localStorage.
     * Returns null if no saved state or error.
     */
    static load() {
        try {
            const raw = localStorage.getItem(LocalStorageObserver.STORAGE_KEY);
            if (!raw) return null;

            const parsed = JSON.parse(raw);
            
            // Version check / Migration logic could go here
            if (parsed.version !== LocalStorageObserver.STORAGE_VERSION) {
                console.warn('Settings version mismatch. Resetting to defaults.');
                return null;
            }

            return parsed.data;
        } catch (e) {
            console.error('Failed to load settings from localStorage:', e);
            return null;
        }
    }
}
