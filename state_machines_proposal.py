"""
Architecture complète des machines à états pour Blokus.

Centralise tous les états : Application, Jeu, Joueurs, Tours.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable

# =============================================================================
# 1. APPLICATION STATE (déjà existant, amélioré)
# =============================================================================

class AppState(Enum):
    """États de l'application."""
    LOADING = "loading"
    INTRO = "intro"
    SETUP = "setup"
    GAME = "game"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    SETTINGS = "settings"
    ERROR = "error"

# =============================================================================
# 2. GAME STATE (amélioré)
# =============================================================================

class GameState(Enum):
    """États du jeu."""
    INITIALIZING = "initializing"
    WAITING_START = "waiting_start"
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"
    ABORTED = "aborted"

# =============================================================================
# 3. PLAYER STATE (nouveau)
# =============================================================================

class PlayerState(Enum):
    """États d'un joueur."""
    WAITING = "waiting"           # En attente de son tour
    THINKING = "thinking"         # IA en train de réfléchir
    PLAYING = "playing"           # En train de jouer/selectionner
    VALIDATING = "validating"     # Validation du coup en cours
    ANIMATING = "animating"       # Animation du coup
    PASSED = "passed"             # A passé son tour
    FINISHED = "finished"         # Plus de pièces/jeu terminé
    DISCONNECTED = "disconnected" # Joueur déconnecté

# =============================================================================
# 4. TURN STATE (nouveau)
# =============================================================================

class TurnState(Enum):
    """États d'un tour."""
    STARTING = "starting"         # Début du tour
    SELECTING_PIECE = "selecting_piece"  # Sélection de pièce
    PLACING_PIECE = "placing_piece"      # Placement de pièce
    VALIDATING_MOVE = "validating_move"  # Validation du coup
    EXECUTING_MOVE = "executing_move"    # Exécution du coup
    ENDING = "ending"             # Fin du tour
    PASSED = "passed"             # Tour passé

# =============================================================================
# 5. MOVE STATE (nouveau)
# =============================================================================

class MoveState(Enum):
    """États d'un mouvement."""
    PROPOSED = "proposed"         # Coup proposé
    VALIDATING = "validating"     # En validation
    VALID = "valid"               # Coup valide
    INVALID = "invalid"           # Coup invalide
    EXECUTED = "executed"         # Coup exécuté
    ANIMATING = "animating"       # Animation en cours
    COMPLETED = "completed"       # Coup terminé
    FAILED = "failed"             # Coup échoué

# =============================================================================
# 6. UI STATE (nouveau)
# =============================================================================

class UIState(Enum):
    """États de l'interface utilisateur."""
    IDLE = "idle"                 # Au repos
    HOVERING = "hovering"         # Survol d'une case
    DRAGGING = "dragging"         # Glisser-déposer
    SELECTING = "selecting"       # Sélection en cours
    ANIMATING = "animating"       # Animation UI
    DISABLED = "disabled"         # Interface désactivée
    LOADING = "loading"           # Chargement

# =============================================================================
# STATE MANAGERS
# =============================================================================

@dataclass
class StateTransition:
    """Représente une transition d'état."""
    from_state: Enum
    to_state: Enum
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None

class StateMachine:
    """Machine à états générique."""
    
    def __init__(self, initial_state: Enum, valid_transitions: Dict[Enum, List[Enum]]):
        self.current_state = initial_state
        self.valid_transitions = valid_transitions
        self.history: List[StateTransition] = []
        self.state_handlers: Dict[Enum, Callable] = {}
        self.transition_handlers: Dict[tuple, Callable] = {}
    
    def can_transition_to(self, new_state: Enum) -> bool:
        """Vérifie si la transition est valide."""
        return new_state in self.valid_transitions.get(self.current_state, [])
    
    def transition_to(self, new_state: Enum, action: str = None, data: Dict[str, Any] = None) -> bool:
        """
        Effectue une transition d'état.
        
        Returns:
            True si la transition a réussi, False sinon
        """
        if not self.can_transition_to(new_state):
            print(f"Invalid transition: {self.current_state} -> {new_state}")
            return False
        
        old_state = self.current_state
        transition = StateTransition(
            from_state=old_state,
            to_state=new_state,
            action=action,
            data=data
        )
        
        # Exécuter les handlers de sortie
        if old_state in self.state_handlers:
            self.state_handlers[old_state](old_state, new_state, "exit")
        
        # Exécuter les handlers de transition
        transition_key = (old_state, new_state)
        if transition_key in self.transition_handlers:
            self.transition_handlers[transition_key](transition)
        
        # Changer l'état
        self.current_state = new_state
        self.history.append(transition)
        
        # Exécuter les handlers d'entrée
        if new_state in self.state_handlers:
            self.state_handlers[new_state](old_state, new_state, "enter")
        
        return True
    
    def add_state_handler(self, state: Enum, handler: Callable):
        """Ajoute un handler pour un état."""
        self.state_handlers[state] = handler
    
    def add_transition_handler(self, from_state: Enum, to_state: Enum, handler: Callable):
        """Ajoute un handler pour une transition."""
        self.transition_handlers[(from_state, to_state)] = handler
    
    def get_state_history(self) -> List[StateTransition]:
        """Retourne l'historique des transitions."""
        return self.history.copy()

# =============================================================================
# PLAYER STATE MACHINE
# =============================================================================

class PlayerStateMachine(StateMachine):
    """Machine à états pour un joueur."""
    
    def __init__(self, player_id: int):
        # Définir les transitions valides
        transitions = {
            PlayerState.WAITING: [PlayerState.THINKING, PlayerState.PLAYING, PlayerState.DISCONNECTED],
            PlayerState.THINKING: [PlayerState.PLAYING, PlayerState.PASSED, PlayerState.DISCONNECTED],
            PlayerState.PLAYING: [PlayerState.VALIDATING, PlayerState.PASSED],
            PlayerState.VALIDATING: [PlayerState.ANIMATING, PlayerState.PLAYING],
            PlayerState.ANIMATING: [PlayerState.WAITING, PlayerState.FINISHED],
            PlayerState.PASSED: [PlayerState.WAITING, PlayerState.FINISHED],
            PlayerState.FINISHED: [],  # État terminal
            PlayerState.DISCONNECTED: [PlayerState.WAITING]  # Peut se reconnecter
        }
        
        super().__init__(PlayerState.WAITING, transitions)
        self.player_id = player_id
    
    def start_turn(self):
        """Démarre le tour du joueur."""
        if self.current_state == PlayerState.WAITING:
            self.transition_to(PlayerState.THINKING, "start_turn")
    
    def make_move(self):
        """Le joueur fait un coup."""
        if self.current_state == PlayerState.THINKING:
            self.transition_to(PlayerState.PLAYING, "make_move")
    
    def validate_move(self):
        """Validation du coup."""
        if self.current_state == PlayerState.PLAYING:
            self.transition_to(PlayerState.VALIDATING, "validate_move")
    
    def execute_move(self):
        """Exécution du coup."""
        if self.current_state == PlayerState.VALIDATING:
            self.transition_to(PlayerState.ANIMATING, "execute_move")
    
    def end_turn(self):
        """Termine le tour."""
        if self.current_state == PlayerState.ANIMATING:
            self.transition_to(PlayerState.WAITING, "end_turn")
    
    def pass_turn(self):
        """Passe le tour."""
        if self.current_state in [PlayerState.THINKING, PlayerState.PLAYING]:
            self.transition_to(PlayerState.PASSED, "pass_turn")
    
    def finish_game(self):
        """Termine le jeu pour ce joueur."""
        self.transition_to(PlayerState.FINISHED, "finish_game")

# =============================================================================
# GAME STATE MACHINE
# =============================================================================

class GameStateMachine(StateMachine):
    """Machine à états pour le jeu."""
    
    def __init__(self):
        # Définir les transitions valides
        transitions = {
            GameState.INITIALIZING: [GameState.WAITING_START, GameState.ABORTED],
            GameState.WAITING_START: [GameState.PLAYING, GameState.ABORTED],
            GameState.PLAYING: [GameState.PAUSED, GameState.FINISHED, GameState.ABORTED],
            GameState.PAUSED: [GameState.PLAYING, GameState.ABORTED],
            GameState.FINISHED: [],  # État terminal
            GameState.ABORTED: []    # État terminal
        }
        
        super().__init__(GameState.INITIALIZING, transitions)
        self.player_machines: Dict[int, PlayerStateMachine] = {}
    
    def add_player(self, player_id: int):
        """Ajoute un joueur avec sa machine à états."""
        self.player_machines[player_id] = PlayerStateMachine(player_id)
    
    def start_game(self):
        """Démarre le jeu."""
        if self.current_state == GameState.WAITING_START:
            self.transition_to(GameState.PLAYING, "start_game")
    
    def pause_game(self):
        """Met le jeu en pause."""
        if self.current_state == GameState.PLAYING:
            self.transition_to(GameState.PAUSED, "pause_game")
    
    def resume_game(self):
        """Reprend le jeu."""
        if self.current_state == GameState.PAUSED:
            self.transition_to(GameState.PLAYING, "resume_game")
    
    def finish_game(self):
        """Termine le jeu."""
        if self.current_state == GameState.PLAYING:
            self.transition_to(GameState.FINISHED, "finish_game")
            # Terminer tous les joueurs
            for machine in self.player_machines.values():
                machine.finish_game()
    
    def abort_game(self):
        """Abandonne le jeu."""
        self.transition_to(GameState.ABORTED, "abort_game")

# =============================================================================
# INTEGRATION AVEC GAMEMANAGER
# =============================================================================

class EnhancedGameManager:
    """GameManager avec machines à états intégrées."""
    
    def __init__(self, players: List[Player], starting_player_index: int = 0):
        # ... (code existant du GameManager) ...
        
        # Ajouter les machines à états
        self.game_state_machine = GameStateMachine()
        
        # Ajouter les joueurs à la machine de jeu
        for player in self.players:
            self.game_state_machine.add_player(player.id)
        
        # Démarrer le jeu
        self.game_state_machine.start_game()
    
    def get_player_state(self, player_id: int) -> PlayerState:
        """Retourne l'état d'un joueur."""
        machine = self.game_state_machine.player_machines.get(player_id)
        return machine.current_state if machine else PlayerState.DISCONNECTED
    
    def get_game_state(self) -> GameState:
        """Retourne l'état du jeu."""
        return self.game_state_machine.current_state
    
    def start_player_turn(self, player_id: int):
        """Démarre le tour d'un joueur."""
        machine = self.game_state_machine.player_machines.get(player_id)
        if machine:
            machine.start_turn()
    
    def execute_player_move(self, player_id: int):
        """Exécute le mouvement d'un joueur."""
        machine = self.game_state_machine.player_machines.get(player_id)
        if machine:
            machine.make_move()
            machine.validate_move()
            machine.execute_move()
            machine.end_turn()

# =============================================================================
# EXEMPLE D'UTILISATION
# =============================================================================

def example_state_machine_usage():
    """Exemple d'utilisation des machines à états."""
    
    # Créer le jeu avec machines à états
    players = [Player(id=0, name="Alice", color="#3b82f6")]
    game_manager = EnhancedGameManager(players)
    
    # Vérifier les états
    print(f"Game state: {game_manager.get_game_state()}")
    print(f"Player state: {game_manager.get_player_state(0)}")
    
    # Démarrer le tour du joueur
    game_manager.start_player_turn(0)
    print(f"Player state after start: {game_manager.get_player_state(0)}")
    
    # Exécuter un coup
    game_manager.execute_player_move(0)
    print(f"Player state after move: {game_manager.get_player_state(0)}")
    
    # Historique des transitions
    player_machine = game_manager.game_state_machine.player_machines[0]
    print("Player state history:")
    for transition in player_machine.get_state_history():
        print(f"  {transition.from_state.value} -> {transition.to_state.value} ({transition.action})")

if __name__ == "__main__":
    example_state_machine_usage()
