# Architecture Unifiée des Joueurs et Machines à États

## 📋 Vue d'Ensemble

Ce document présente une refactoring majeure de l'architecture des joueurs dans Blokus RL pour centraliser la logique, éliminer la duplication et introduire des machines à états robustes.

---

## 🎯 Objectifs

### Problèmes Actuels
- **Logique fragmentée** : Player dans le moteur, PlayerConfig dans l'API, PlayerState dans l'API, et objets joueurs dans le frontend
- **Mapping ID↔Index complexe** : Confusion entre `player.id` et `player.index`
- **Duplication des couleurs** : Couleurs définies à plusieurs endroits
- **Pas de validation d'états** : Transitions non contrôlées
- **Code éparpillé** : Logique des joueurs dispersée partout

### Solutions Proposées
- **Classe Player unifiée** : Une seule classe utilisée partout
- **GameManager centralisé** : Gestion de l'ordre et des tours
- **Machines à états** : Validation des transitions et historique
- **Factory pattern** : Création standardisée des joueurs
- **Single Source of Truth** : Une source de vérité pour les données joueur

---

## 🏗️ Architecture Proposée

### 1. Classe Player Unifiée

```python
@dataclass
class Player:
    # === IDENTITÉ ===
    id: int
    name: str
    color: str  # Hex color comme "#3b82f6"
    type: PlayerType  # HUMAN, AI, SHARED
    persona: Optional[str]  # "random", "aggressive", etc.
    
    # === ÉTAT DU JEU ===
    remaining_pieces: Set[PieceType]
    has_passed: bool
    last_piece_was_monomino: bool
    status: PlayerStatus  # WAITING, PLAYING, PASSED, etc.
    
    # === MÉTADONNÉES ===
    score: int
    turn_order: Optional[int]
    
    # === MÉTHODES ===
    def play_piece(self, piece_type: PieceType) -> bool
    def pass_turn(self) -> None
    def calculate_score(self) -> int
    def to_dict() -> Dict[str, Any]
```

**Avantages :**
- ✅ Centralise toutes les informations d'un joueur
- ✅ Méthodes directement sur l'objet
- ✅ Sérialisation/Deserialisation intégrée
- ✅ Propriétés calculées (`display_name`, `is_ai`, etc.)

### 2. GameManager

```python
@dataclass
class GameManager:
    players: List[Player]  # Ordre = ordre de jeu
    current_player_index: int
    turn_history: List[int]
    game_finished: bool
    
    # === GESTION DES TOURS ===
    def next_turn(self) -> Player
    def set_starting_player(self, player_id: int)
    def get_current_player(self) -> Player
    
    # === ORDRES DIFFÉRENTS ===
    def get_play_order(self) -> List[Player]
    def get_score_order(self) -> List[Player]
    def get_turn_order_from_current(self) -> List[Player]
    
    # === UTILITAIRES ===
    def get_player_by_id(self, player_id: int) -> Optional[Player]
    def is_game_over(self) -> bool
    def get_winner(self) -> Optional[Player]
```

**Avantages :**
- ✅ Ordre des joueurs = ordre dans la liste (pas de mapping)
- ✅ Plusieurs ordres disponibles (jeu, score, tour)
- ✅ Gestion centralisée des transitions
- ✅ Historique des tours intégré

### 3. Factory Pattern

```python
class PlayerFactory:
    @classmethod
    def create_human_player(cls, id: int, name: str, color: str = None) -> Player
    
    @classmethod
    def create_ai_player(cls, id: int, persona: str, color: str = None) -> Player
    
    @classmethod
    def create_shared_player(cls, id: int, color: str = None) -> Player
    
    @classmethod
    def create_players_from_config(cls, configs: List[Dict]) -> List[Player]

class GameManagerFactory:
    @classmethod
    def create_from_config(cls, configs: List[Dict], starting_player_id: int) -> GameManager
    
    @classmethod
    def create_standard_game(cls, num_players: int, starting_player_id: int) -> GameManager
```

**Avantages :**
- ✅ Création standardisée
- ✅ Couleurs par défaut cohérentes
- ✅ Validation des configurations
- ✅ Code réutilisable

---

## 🔄 Machines à États

### 1. Player State Machine

```python
class PlayerState(Enum):
    WAITING = "waiting"           # En attente de son tour
    THINKING = "thinking"         # IA en train de réfléchir
    PLAYING = "playing"           # En train de jouer
    VALIDATING = "validating"     # Validation du coup
    ANIMATING = "animating"       # Animation du coup
    PASSED = "passed"             # A passé son tour
    FINISHED = "finished"         # Plus de pièces
    DISCONNECTED = "disconnected" # Déconnecté

# Transitions valides :
# WAITING → THINKING → PLAYING → VALIDATING → ANIMATING → WAITING
# WAITING/THINKING/PLAYING → PASSED → WAITING
# Any → FINISHED (terminal)
# Any → DISCONNECTED → WAITING
```

### 2. Game State Machine

```python
class GameState(Enum):
    INITIALIZING = "initializing"
    WAITING_START = "waiting_start"
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"
    ABORTED = "aborted"

# Transitions valides :
# INITIALIZING → WAITING_START/ABORTED
# WAITING_START → PLAYING/ABORTED
# PLAYING → PAUSED/FINISHED/ABORTED
# PAUSED → PLAYING/ABORTED
```

### 3. State Machine Générique

```python
class StateMachine:
    def can_transition_to(self, new_state: Enum) -> bool
    def transition_to(self, new_state: Enum, action: str, data: Dict) -> bool
    def add_state_handler(self, state: Enum, handler: Callable)
    def add_transition_handler(self, from_state: Enum, to_state: Enum, handler: Callable)
    def get_state_history(self) -> List[StateTransition]
```

**Avantages :**
- ✅ Validation des transitions
- ✅ Historique complet
- ✅ Handlers automatiques
- ✅ Débogage facilité

---

## 📊 Flux d'Utilisation

### 1. Configuration Initiale

```python
# Configuration depuis le menu
config = [
    {"name": "Alice", "type": "human"},
    {"name": "Bob", "type": "ai", "persona": "random"},
    {"name": "Charlie", "type": "human"},
    {"name": "Diana", "type": "ai", "persona": "aggressive"}
]

# Création du GameManager
game_manager = GameManagerFactory.create_from_config(config, starting_player_id=2)
```

### 2. Tour par Tour

```python
# Tour actuel
current = game_manager.current_player
print(f"C'est le tour de: {current.display_name}")  # "Charlie"

# Passer au tour suivant (gère automatiquement les joueurs qui ont passé)
next_player = game_manager.next_turn()

# Ordre de jeu (reste [0,1,2,3] mais commence à l'index 2)
play_order = game_manager.get_play_order()
```

### 3. Machines à États

```python
# Démarrer le tour d'un joueur
player_machine = game_manager.get_player_machine(current.id)
player_machine.start_turn()  # WAITING → THINKING

# Jouer un coup
player_machine.make_move()      # THINKING → PLAYING
player_machine.validate_move()  # PLAYING → VALIDATING
player_machine.execute_move()   # VALIDATING → ANIMATING
player_machine.end_turn()       # ANIMATING → WAITING
```

---

## 🔧 Intégration avec Code Existant

### Moteur de Jeu (Python)

```python
# Avant
class Game:
    def __init__(self, num_players, starting_player_idx):
        self.num_players = num_players
        self.current_player_idx = starting_player_idx
        self.players = [Player(id=i) for i in range(num_players)]

# Après
class Game:
    def __init__(self, player_configs, starting_player_id):
        self.game_manager = GameManagerFactory.create_from_config(
            player_configs, starting_player_id
        )
    
    @property
    def current_player(self) -> Player:
        return self.game_manager.current_player
    
    def play_move(self, move: Move) -> bool:
        # ... logique existante ...
        self.game_manager.next_turn()
        return True
```

### API (FastAPI)

```python
# Avant
@app.post("/game/new")
def create_game(request: CreateGameRequest):
    game = Game(num_players=request.num_players, starting_player_idx=request.start_player)
    return {"game_state": map_game_to_state(game)}

# Après
@app.post("/game/new")
def create_game(request: CreateGameRequest):
    game_manager = GameManagerFactory.create_from_config(
        request.players, request.start_player
    )
    return {"game_state": game_manager.to_dict()}
```

### Frontend (JavaScript)

```javascript
// Avant
class Game {
    constructor(config) {
        this.players = config.players;
        this.currentPlayer = config.startPlayer;
        this.currentPlayerIndex = config.startPlayer;
    }
    
    nextTurn() {
        // Logique complexe pour trouver le prochain joueur
        do {
            this.currentPlayerIndex = (this.currentPlayerIndex + 1) % this.players.length;
        } while (this.players[this.currentPlayerIndex].hasPassed);
        this.currentPlayer = this.currentPlayerIndex;
    }
}

// Après
class Game {
    constructor(config) {
        this.gameManager = new GameManager(config.players, config.startPlayer);
    }
    
    getCurrentPlayer() {
        return this.gameManager.currentPlayer;
    }
    
    nextTurn() {
        return this.gameManager.nextTurn();
    }
    
    getScoreOrder() {
        return this.gameManager.getScoreOrder();
    }
}
```

---

## 🎯 Avantages de l'Architecture

### 1. **Centralisation**
- Une seule classe `Player` utilisée partout
- Plus de duplication de logique
- Single Source of Truth

### 2. **Simplicité**
- `game_manager.current_player` au lieu de `game.players[game.current_player_idx]`
- Ordre des joueurs = ordre dans la liste
- Plus de mapping ID↔Index

### 3. **Robustesse**
- Machines à états valident les transitions
- Historique complet pour le débogage
- États cohérents garantis

### 4. **Extensibilité**
- Ajouter de nouveaux types de joueurs facilement
- Nouveaux ordres (par date, par type, etc.)
- Handlers personnalisés par état

### 5. **Maintenabilité**
- Code auto-documenté
- Logique centralisée
- Tests plus simples

---

## 📋 Plan d'Implémentation

### Phase 1 : Player Unifié
- [ ] Créer la nouvelle classe `Player` dans `blokus-engine/src/blokus/player.py`
- [ ] Créer `PlayerFactory`
- [ ] Tests unitaires pour `Player` et `PlayerFactory`
- [ ] Migrer le moteur de jeu

### Phase 2 : GameManager
- [ ] Implémenter `GameManager`
- [ ] Créer `GameManagerFactory`
- [ ] Tests unitaires pour `GameManager`
- [ ] Intégrer avec le moteur de jeu

### Phase 3 : API
- [ ] Mettre à jour les modèles API
- [ ] Modifier les endpoints pour utiliser `GameManager`
- [ ] Tests d'intégration API
- [ ] Migration des données

### Phase 4 : Machines à États
- [ ] Implémenter `StateMachine` générique
- [ ] Créer `PlayerStateMachine`
- [ ] Créer `GameStateMachine`
- [ ] Tests des machines à états

### Phase 5 : Frontend
- [ ] Adapter les classes JavaScript
- [ ] Mettre à jour les handlers UI
- [ ] Tests frontend
- [ ] Integration complète

### Phase 6 : Tests Finaux
- [ ] Tests d'intégration complets
- [ ] Tests de régression
- [ ] Tests de performance
- [ ] Documentation mise à jour

---

## 🔍 Migration Strategy

### 1. **Approche Incremental**
- Implémenter en parallèle de l'existant
- Basculer progressivement
- Tests de régression à chaque étape

### 2. **Compatibilité**
- Garder les anciennes API pendant la transition
- Convertir les anciens formats vers les nouveaux
- Tests de compatibilité

### 3. **Rollback**
- Conserver l'ancien code
- Tests de rollback
- Documentation de migration

---

## 📊 Impact sur le Code

### Fichiers Modifiés

#### Moteur (`blokus-engine/`)
- `src/blokus/player.py` - Refactor complet
- `src/blokus/game.py` - Intégration GameManager
- `tests/test_player.py` - Nouveaux tests
- `tests/test_game.py` - Mise à jour

#### API (`blokus-server/`)
- `api/models.py` - Nouveaux modèles
- `main.py` - Intégration GameManager
- `tests/` - Tests API mis à jour

#### Frontend (`blokus-web/`)
- `js/game.js` - Intégration GameManager
- `js/setup.js` - Utilisation PlayerFactory
- `js/state.js` - Machines à états
- `tests/` - Tests frontend

### Fichiers Nouveaux

#### Moteur
- `src/blokus/game_manager.py`
- `src/blokus/state_machines.py`
- `tests/test_game_manager.py`
- `tests/test_state_machines.py`

#### Documentation
- `docs/player_architecture.md` (ce document)
- `docs/migration_guide.md`
- `docs/state_machines.md`

---

## 🎯 Conclusion

Cette refactoring majeure va :

1. **Éliminer la fragmentation** de la logique des joueurs
2. **Centraliser la gestion** de l'ordre et des états
3. **Introduire la robustesse** des machines à états
4. **Simplifier le code** et le rendre plus maintenable
5. **Faciliter l'extensibilité** future

Le résultat sera une architecture plus propre, plus robuste et plus facile à comprendre et maintenir.

---

## 📚 Références

- [Design Decisions](design_decisions.md)
- [Implementation Roadmap](implementation_roadmap.md)
- [Current Architecture Analysis](modeling_analysis.md)

---

*Document créé le 1er janvier 2026*
*Auteur : Cascade AI Assistant*
*Version : 1.0*
