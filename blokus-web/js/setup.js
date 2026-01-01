export class SetupManager {
    constructor(onStartGame) {
        this.onStartGame = onStartGame;
        this.modal = document.getElementById('setup-modal');
        this.playersConfigContainer = document.getElementById('players-config');
        this.playerCountBtns = document.querySelectorAll('.toggle-btn[data-players]');
        this.startBtn = document.getElementById('btn-start-game');

        this.playerCount = 4;
        this.DEFAULT_NAMES = ['Joueur 1', 'Joueur 2', 'Joueur 3', 'Joueur 4'];
        this.COLORS = ['#3b82f6', '#22c55e', '#eab308', '#ef4444']; // Blue, Green, Yellow, Red

        this.init();
    }

    init() {
        this.renderPlayerInputs();

        // Event Listeners for Player Count
        this.playerCountBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const count = parseInt(e.target.dataset.players);
                this.setPlayerCount(count);
            });
        });

        // Event Listener for Start Game
        this.startBtn.addEventListener('click', () => {
            this.startGame();
        });
    }

    setPlayerCount(count) {
        this.playerCount = count;

        // Update UI buttons
        this.playerCountBtns.forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.players) === count);
        });

        this.renderPlayerInputs();
    }

    renderPlayerInputs() {
        this.playersConfigContainer.innerHTML = '';

        for (let i = 0; i < this.playerCount; i++) {
            const row = document.createElement('div');
            row.className = `player-config-row p${i}`;

            // Color Indicator
            const colorIndicator = document.createElement('div');
            colorIndicator.className = 'color-indicator';
            colorIndicator.style.backgroundColor = this.COLORS[i];

            // Name Input
            const nameInput = document.createElement('input');
            nameInput.type = 'text';
            nameInput.className = 'setup-input name-input';
            nameInput.value = this.DEFAULT_NAMES[i];
            nameInput.placeholder = `Nom Joueur ${i + 1}`;

            // Type Select (Human/IA)
            const typeSelect = document.createElement('select');
            typeSelect.className = 'setup-input type-select';
            typeSelect.innerHTML = `
                <option value="human">Humain</option>
                <option value="ai">IA</option>
            `;

            // Persona Select (Hidden by default)
            const personaSelect = document.createElement('select');
            personaSelect.className = 'setup-input persona-select';
            personaSelect.innerHTML = `
                <option value="random">Aléatoire</option>
                <option value="aggressive">Agressif</option>
                <option value="defensive">Défensif</option>
                <option value="efficient">Efficace</option>
            `;
            personaSelect.style.display = 'none';

            // Show/Hide Persona based on Type
            typeSelect.addEventListener('change', (e) => {
                personaSelect.style.display = e.target.value === 'ai' ? 'block' : 'none';
            });

            row.appendChild(colorIndicator);
            row.appendChild(nameInput);
            row.appendChild(typeSelect);
            row.appendChild(personaSelect);

            this.playersConfigContainer.appendChild(row);
        }

        // Update Start Player Select options
        const startSelect = document.getElementById('start-player-select');
        startSelect.innerHTML = '<option value="random">Aléatoire</option>';
        for (let i = 0; i < this.playerCount; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = `Joueur ${i + 1}`; // Will be updated if names change? No, keep simple
            startSelect.appendChild(option);
        }
    }

    startGame() {
        const players = [];
        const rows = this.playersConfigContainer.querySelectorAll('.player-config-row');

        rows.forEach((row, index) => {
            const name = row.querySelector('.name-input').value || `Joueur ${index + 1}`;
            const type = row.querySelector('.type-select').value;
            const persona = row.querySelector('.persona-select').value;

            players.push({
                id: index,
                name: name,
                color: this.COLORS[index],
                type: type,
                persona: type === 'ai' ? persona : null
            });
        });

        const startPlayerVal = document.getElementById('start-player-select').value;
        const startPlayer = startPlayerVal === 'random' ? Math.floor(Math.random() * this.playerCount) : parseInt(startPlayerVal);

        // Handle 3-Player mode: Add 4th Shared Player
        let finalPlayerCount = this.playerCount;
        if (this.playerCount === 3) {
            players.push({
                id: 3,
                name: 'Neutre (Partagé)',
                color: this.COLORS[3], // Red usually
                type: 'SHARED',
                persona: null
            });
            finalPlayerCount = 4;
        }

        const config = {
            playerCount: finalPlayerCount,
            players: players,
            startPlayer: startPlayer
        };

        this.modal.classList.add('hidden');
        this.onStartGame(config);
    }

    show() {
        this.modal.classList.remove('hidden');
    }
}
