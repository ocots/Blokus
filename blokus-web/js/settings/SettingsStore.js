/**
 * SettingsStore (Subject)
 * Handles the configuration state of the game setup.
 * Validates updates and notifies observers (persistence, UI).
 */
export class SettingsStore {
    constructor(initialState = {}) {
        this.observers = [];
        
        // Default State
        this.state = {
            playerCount: 4,
            twoPlayerMode: 'duo', // 'duo' | 'standard'
            startPlayer: 'random', // 'random' | 0 | 1 | 2 | 3
            colorblindMode: false,
            players: this._createDefaultPlayers(4),
            ...initialState
        };

        // Ensure players array is valid if loaded from state
        if (initialState.players) {
            this.state.players = this._mergePlayers(this._createDefaultPlayers(4), initialState.players);
        }
    }

    /**
     * Subscribe an observer to state changes.
     * Observer must have an update(state) method.
     */
    subscribe(observer) {
        this.observers.push(observer);
    }

    /**
     * Unsubscribe an observer.
     */
    unsubscribe(observer) {
        this.observers = this.observers.filter(obs => obs !== observer);
    }

    /**
     * Get current state (immutable copy).
     */
    getState() {
        return JSON.parse(JSON.stringify(this.state));
    }

    /**
     * Update state with partial data.
     * Validates and merges changes, then notifies observers.
     */
    update(partialState) {
        const nextState = { ...this.state, ...partialState };

        // Specific Validation Logic
        if (partialState.playerCount) {
             const count = parseInt(partialState.playerCount);
             if (count !== 2 && count !== 4) {
                 console.warn(`Invalid player count: ${count}. Ignoring.`);
                 return;
             }
             nextState.playerCount = count;
        }

        if (partialState.players) {
             nextState.players = this._mergePlayers(this.state.players, partialState.players);
        }
        
        // Merge remaining simple fields
        if (partialState.twoPlayerMode) nextState.twoPlayerMode = partialState.twoPlayerMode;
        if (partialState.startPlayer !== undefined) nextState.startPlayer = partialState.startPlayer; // check undefined for 0 value
        if (typeof partialState.colorblindMode === 'boolean') nextState.colorblindMode = partialState.colorblindMode;

        this.state = nextState;
        this._notify();
    }
    
    /**
     * Update specific player configuration
     */
    updatePlayer(index, changes) {
        const players = [...this.state.players];
        if (players[index]) {
            players[index] = { ...players[index], ...changes };
            this.update({ players });
        }
    }

    /* Private Methods */

    _notify() {
        const state = this.getState();
        this.observers.forEach(observer => observer.update(state));
    }

    _createDefaultPlayers(count = 4) {
        const colors = ['#3b82f6', '#22c55e', '#eab308', '#ef4444'];
        return Array.from({ length: 4 }, (_, i) => ({
            id: i,
            name: `Joueur ${i + 1}`,
            color: colors[i],
            type: 'human', // 'human' | 'ai'
            persona: 'random' // 'random' | 'aggressive' | 'defensive' | 'efficient'
        }));
    }
    
    _mergePlayers(currentPlayers, newPlayers) {
         // Merge new config into current players while preserving defaults for missing fields
         // newPlayers might be sparse or have fewer items
         const merged = [...currentPlayers];
         newPlayers.forEach((p, i) => {
             if (merged[i]) {
                 merged[i] = { ...merged[i], ...p };
             }
         });
         return merged;
    }
}
