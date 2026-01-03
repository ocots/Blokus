import { SettingsStore } from './settings/SettingsStore.js';
import { LocalStorageObserver } from './settings/LocalStorageObserver.js';

export class SetupManager {
    constructor(onStartGame) {
        this.onStartGame = onStartGame;
        this.modal = document.getElementById('setup-modal');
        this.playersConfigContainer = document.getElementById('players-config');
        this.playerCountBtns = document.querySelectorAll('.toggle-btn[data-players]');
        this.startBtn = document.getElementById('btn-start-game');

        // New Mode Selector Elements
        this.modeSelector = document.getElementById('two-player-mode-selector');
        this.modeBtns = document.querySelectorAll('.mode-btn');

        // Initialize Store with persisted state
        const savedState = LocalStorageObserver.load();
        this.store = new SettingsStore(savedState || {});

        // Subscribe Observer for persistence
        this.store.subscribe(new LocalStorageObserver());

        this.DEFAULT_NAMES = ['Joueur 1', 'Joueur 2', 'Joueur 3', 'Joueur 4'];
        this.COLORS = ['#3b82f6', '#22c55e', '#eab308', '#ef4444']; // Blue, Green, Yellow, Red

        this.init();
    }

    init() {
        // Initial Render based on Store State
        const state = this.store.getState();
        this.setPlayerCountUI(state.playerCount);
        this.setModeUI(state.twoPlayerMode);

        // If we have saved players, we might need to rely on renderPlayerInputs called within setPlayerCountUI
        // But setPlayerCountUI calls renderPlayerInputs. We need to make sure renderPlayerInputs uses the store.

        // Event Listeners for Player Count
        this.playerCountBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const count = parseInt(e.target.dataset.players);
                // Update Store
                this.store.update({ playerCount: count });
                // Update UI
                this.setPlayerCountUI(count);
            });
        });

        // Event Listeners for Mode Selector
        this.modeBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mode = e.target.dataset.mode;
                // Update Store
                this.store.update({ twoPlayerMode: mode });
                // Update UI
                this.setModeUI(mode);
            });
        });

        // Tooltip logic
        const helpIcon = this.modeSelector.querySelector('.help-icon');
        const tooltip = this.modeSelector.querySelector('.mode-tooltip');
        const duoInfo = tooltip.querySelector('.duo-info');
        const standardInfo = tooltip.querySelector('.standard-info');

        helpIcon.addEventListener('mouseenter', () => {
            tooltip.style.display = 'block';
            const currentMode = this.store.getState().twoPlayerMode;
            // Show info based on current selection
            if (currentMode === 'duo') {
                duoInfo.style.display = 'block';
                standardInfo.style.display = 'none';
            } else {
                duoInfo.style.display = 'none';
                standardInfo.style.display = 'block';
            }
        });

        helpIcon.addEventListener('mouseleave', () => {
            tooltip.style.display = 'none';
        });

        // Colorblind toggle
        const checkbox = document.getElementById('colorblind-mode');
        if (checkbox) {
            checkbox.checked = state.colorblindMode;
            checkbox.addEventListener('change', (e) => {
                this.store.update({ colorblindMode: e.target.checked });
            });
        }

        // Start Player Select
        const startSelect = document.getElementById('start-player-select');
        if (startSelect) {
            startSelect.value = state.startPlayer; // might be 'random' or '0', '1'...
            startSelect.addEventListener('change', (e) => {
                this.store.update({ startPlayer: e.target.value });
            });
        }

        // Event Listener for Start Game
        this.startBtn.addEventListener('click', () => {
            this.startGame();
        });
    }

    setModeUI(mode) {
        this.modeBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });
    }

    setPlayerCountUI(count) {
        // Update UI buttons
        this.playerCountBtns.forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.players) === count);
        });

        // Show/Hide Mode Selector
        if (count === 2) {
            this.modeSelector.style.display = 'block';
        } else {
            this.modeSelector.style.display = 'none';
        }

        this.renderPlayerInputs();
    }

    renderPlayerInputs() {
        this.playersConfigContainer.innerHTML = '';
        const state = this.store.getState();
        const count = state.playerCount;
        const players = state.players;

        for (let i = 0; i < count; i++) {
            const playerConfig = players[i];
            const row = document.createElement('div');
            row.className = `player-config-row p${i}`;

            // Color Indicator
            const colorIndicator = document.createElement('div');
            colorIndicator.className = 'color-indicator';
            colorIndicator.style.backgroundColor = this.COLORS[i];

            // Type Select (Human/IA)
            const typeSelect = document.createElement('select');
            typeSelect.className = 'setup-input type-select';
            typeSelect.innerHTML = `
                <option value="human" ${playerConfig.type === 'human' ? 'selected' : ''}>Humain</option>
                <option value="ai" ${playerConfig.type === 'ai' ? 'selected' : ''}>IA</option>
            `;

            typeSelect.addEventListener('change', (e) => {
                const newType = e.target.value;
                this.store.updatePlayer(i, { type: newType });
                // Update visibility immediately
                const isAI = newType === 'ai';
                nameInput.style.display = isAI ? 'none' : 'block';
                personaSelect.style.display = isAI ? 'block' : 'none';
            });

            // Input Wrapper for Name/Persona (Right side)
            const inputWrapper = document.createElement('div');
            inputWrapper.className = 'input-wrapper';
            inputWrapper.style.display = 'flex';
            inputWrapper.style.flex = '1';

            // Name Input
            const nameInput = document.createElement('input');
            nameInput.type = 'text';
            nameInput.className = 'setup-input name-input';
            nameInput.value = playerConfig.name;
            nameInput.placeholder = `Nom Joueur ${i + 1}`;
            nameInput.style.width = '100%';

            nameInput.addEventListener('input', (e) => {
                this.store.updatePlayer(i, { name: e.target.value });
            });

            // Persona Select (Hidden by default)
            const personaSelect = document.createElement('select');
            personaSelect.className = 'setup-input persona-select';

            const personas = [
                { val: 'random', label: 'Aléatoire', title: 'Joue de manière totalement aléatoire. Niveau : Débutant' },
                { val: 'aggressive', label: 'Agressif', title: 'Cherche à bloquer l\'adversaire. Niveau : Moyen' },
                { val: 'defensive', label: 'Défensif', title: 'Privilégie sa propre sécurité. Niveau : Moyen' },
                { val: 'efficient', label: 'Efficace', title: 'Cherche à maximiser ses points. Niveau : Difficile' }
            ];

            personaSelect.innerHTML = personas.map(p =>
                `<option value="${p.val}" title="${p.title}" ${playerConfig.persona === p.val ? 'selected' : ''}>${p.label}</option>`
            ).join('');

            personaSelect.style.width = '100%';

            personaSelect.addEventListener('change', (e) => {
                this.store.updatePlayer(i, { persona: e.target.value });
            });

            // Set initial visibility
            const isAI = playerConfig.type === 'ai';
            nameInput.style.display = isAI ? 'none' : 'block';
            personaSelect.style.display = isAI ? 'block' : 'none';
            personaSelect.style.display = isAI ? 'block' : 'none';

            inputWrapper.appendChild(nameInput);
            inputWrapper.appendChild(personaSelect);

            row.appendChild(colorIndicator);
            row.appendChild(typeSelect);     // Type first (left)
            row.appendChild(inputWrapper);   // Name/Persona second (right, takes remaining space)

            this.playersConfigContainer.appendChild(row);
        }

        // Update Start Player Select options
        const startSelect = document.getElementById('start-player-select');
        // Save current value to restore if possible, though initialized in init
        const currentValue = startSelect.value;

        startSelect.innerHTML = '<option value="random">Aléatoire</option>';
        for (let i = 0; i < count; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = `Joueur ${i + 1}`;
            if (String(i) === String(state.startPlayer)) option.selected = true;
            startSelect.appendChild(option);
        }
        if (state.startPlayer === 'random') startSelect.value = 'random';
    }

    startGame() {
        // Just read from store, cleaner!
        const state = this.store.getState();
        const count = state.playerCount;

        const players = [];
        for (let i = 0; i < count; i++) {
            const p = state.players[i];
            let name = p.name || `Joueur ${i + 1}`;

            // For AI, force name to be persona-based if needed, or keep stored name?
            // Existing logic overrode name for AI. Let's keep consistency.
            if (p.type === 'ai') {
                // Map persona to display name is done in backend usually, but here we can set a default
                const personaLabels = {
                    'random': 'Bot Aléatoire',
                    'aggressive': 'Bot Agressif',
                    'defensive': 'Bot Défensif',
                    'efficient': 'Bot Efficace'
                };
                name = personaLabels[p.persona] || p.name;
            }

            players.push({
                id: i,
                name: name,
                color: this.COLORS[i],
                type: p.type,
                persona: p.type === 'ai' ? p.persona : null
            });
        }

        let startPlayer = state.startPlayer;
        if (startPlayer === 'random') {
            startPlayer = Math.floor(Math.random() * count);
        } else {
            startPlayer = parseInt(startPlayer);
        }

        const config = {
            playerCount: count,
            players: players,
            startPlayer: startPlayer,
            twoPlayerMode: (count === 2) ? state.twoPlayerMode : null,
            settings: {
                colorblindMode: state.colorblindMode
            }
        };

        this.modal.classList.add('hidden');
        this.onStartGame(config);
    }

    show() {
        this.modal.classList.remove('hidden');
    }
}

