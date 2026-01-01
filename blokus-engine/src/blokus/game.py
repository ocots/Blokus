from dataclasses import dataclass
from typing import List, Optional, Tuple, Set
from enum import Enum
import numpy as np

from blokus.pieces import Piece, PieceType, PIECES, get_piece
from blokus.board import Board, BOARD_SIZE
from blokus.player import Player
from blokus.player_factory import PlayerFactory
from blokus.game_manager import GameManager
from blokus.rules import is_valid_placement, get_valid_placements, has_valid_move


class GameStatus(Enum):
    """Game status."""
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


@dataclass
class Move:
    """Represents a move in the game."""
    player_id: int
    piece_type: PieceType
    orientation: int
    row: int
    col: int
    
    def get_piece(self) -> Piece:
        """Get the piece object for this move."""
        return get_piece(self.piece_type, self.orientation)


class Game:
    """
    Blokus game manager.
    
    Handles game state, turns, move validation, and scoring.
    Now uses GameManager for player and turn management.
    """
    def __init__(
        self, 
        num_players: int = 4,
        board: Optional[Board] = None,
        players: Optional[List[Player]] = None,
        starting_player_idx: int = 0,
        move_history: Optional[List[Move]] = None,
        status: GameStatus = GameStatus.IN_PROGRESS,
        game_manager: Optional[GameManager] = None
    ):
        self.board = board or Board()
        self.move_history = move_history or []
        self.status = status
        
        # Use GameManager for player management
        if game_manager is not None:
            self.game_manager = game_manager
        elif players:
            # Create GameManager from provided players
            self.game_manager = GameManager(players, starting_player_idx)
        else:
            # Create default players with GameManager
            default_players = PlayerFactory.create_standard_players(num_players)
            self.game_manager = GameManager(default_players, starting_player_idx)
    
    # Convenience properties for backward compatibility
    @property
    def players(self) -> List[Player]:
        """Get players list."""
        return self.game_manager.players
    
    @property
    def num_players(self) -> int:
        """Get number of players."""
        return self.game_manager.player_count
    
    @property
    def current_player_idx(self) -> int:
        """Get current player index."""
        return self.game_manager.current_player_index
    
    @property
    def current_player(self) -> Player:
        """Get current player."""
        return self.game_manager.current_player
    
    @property
    def turn_number(self) -> int:
        """Current turn number (0-indexed)."""
        return len(self.move_history)
    
    def is_first_move(self, player_id: int) -> bool:
        """Check if this is the player's first move."""
        return not any(m.player_id == player_id for m in self.move_history)
    
    def get_valid_moves(self, player_id: Optional[int] = None) -> List[Move]:
        """
        Get all valid moves for a player.
        
        Args:
            player_id: Player to check (default: current player)
        
        Returns:
            List of valid Move objects
        """
        if player_id is None:
            player_id = self.current_player_idx
        
        player = self.players[player_id]
        is_first = self.is_first_move(player_id)
        valid_moves: List[Move] = []
        
        for piece_type in player.remaining_pieces:
            # Iterate over all pre-calculated orientations for this piece type
            for piece in PIECES[piece_type]:
                positions = get_valid_placements(self.board, piece, player_id, is_first)
                for row, col in positions:
                    valid_moves.append(Move(
                        player_id=player_id,
                        piece_type=piece_type,
                        orientation=piece.orientation_id,
                        row=row,
                        col=col
                    ))
        
        return valid_moves
    
    def is_valid_move(self, move: Move) -> bool:
        """Check if a move is valid."""
        player = self.players[move.player_id]
        
        # Check piece is available
        if move.piece_type not in player.remaining_pieces:
            return False
        
        # Check current player's turn
        if move.player_id != self.current_player_idx:
            return False
        
        piece = move.get_piece()
        is_first = self.is_first_move(move.player_id)
        
        return is_valid_placement(self.board, piece, move.row, move.col, move.player_id, is_first)
    
    def play_move(self, move: Move) -> bool:
        """
        Execute a move.
        
        Args:
            move: The move to execute
        
        Returns:
            True if move was successful, False otherwise
        """
        if not self.is_valid_move(move):
            print(f"Invalid move: {move}") # Debug info
            return False
        
        piece = move.get_piece()
        player = self.players[move.player_id]
        
        # Place piece on board
        success = self.board.place_piece(piece, move.row, move.col, move.player_id)
        if not success:
            print(f"Board placement failed for move: {move}")
            return False
            
        # Update player state
        player.remaining_pieces.remove(move.piece_type)
        player.last_piece_was_monomino = (move.piece_type == PieceType.I1)
        
        # Record move
        self.move_history.append(move)
        
        # Advance turn
        self._next_turn()
        
        return True
    
    def pass_turn(self) -> bool:
        """
        Current player passes their turn.
        
        Returns:
            True if pass was successful
        """
        player = self.current_player
        
        # Check if player actually has no valid moves
        # (In standard rules, you must play if you can)
        valid_moves = self.get_valid_moves()
        if valid_moves:
            # Uncomment to enforce rules strictly
            # return False
            pass 
        
        player.has_passed = True
        self._next_turn()
        return True
    
    def force_pass(self) -> None:
        """Force current player to pass (even if they have moves)."""
        self.current_player.has_passed = True
        self._next_turn()
    
    def _next_turn(self) -> None:
        """Advance to next player using GameManager."""
        # Check if game is over
        if self._check_game_over():
            self.status = GameStatus.FINISHED
            return
        
        # Auto-pass players with no valid moves
        current = self.current_player
        if not current.has_passed and current.remaining_pieces:
            valid_moves = self.get_valid_moves()
            if not valid_moves:
                current.has_passed = True
        
        # Use GameManager to advance turn
        self.game_manager.next_turn()
        
        # Check if game is finished
        if self.game_manager.is_game_over():
            self.status = GameStatus.FINISHED
    
    def _check_game_over(self) -> bool:
        """Check if game is over (all players have passed)."""
        return all(p.has_passed for p in self.players)
    
    def get_scores(self) -> List[int]:
        """
        Calculate scores for all players.
        
        Scoring:
        - Each remaining square = -1 point
        - All pieces placed = +15 bonus
        - Last piece was monomino (if all placed) = +5 bonus
        """
        scores = []
        
        for player in self.players:
            score = -player.squares_remaining
            
            if player.pieces_count == 0:
                score += 15  # All pieces placed bonus
                if player.last_piece_was_monomino:
                    score += 5  # Monomino last bonus
            
            scores.append(score)
        
        return scores
    
    def get_winner(self) -> Optional[int]:
        """Get the ID of the winning player (or None if tie)."""
        scores = self.get_scores()
        max_score = max(scores)
        winners = [i for i, s in enumerate(scores) if s == max_score]
        if len(winners) == 1:
            return winners[0]
        return None  # Tie or multiple winners
    
    def get_rankings(self) -> List[int]:
        """Get player rankings (0 = first place)."""
        scores = self.get_scores()
        # Sort indices by score (descending)
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        rankings = [0] * len(scores)
        for rank, player_idx in enumerate(ranked):
            rankings[player_idx] = rank
        return rankings
    
    def get_state_tensor(self) -> "np.ndarray":
        """
        Get state representation for RL.
        Returns a (20, 20, num_channels) tensor.
        """
        # Currently simplified: just player occupancy
        channels = []
        
        # One channel per player (occupancy)
        for player_id in range(self.num_players):
            channel = (self.board.grid == player_id + 1).astype(np.float32)
            channels.append(channel)
        
        return np.stack(channels, axis=-1)
    
    def copy(self) -> "Game":
        """Create a deep copy of the game."""
        # Create new players manually to avoid reference issues
        new_players = [
            Player(
                id=p.id,
                name=p.name,
                color=p.color,
                type=p.type,
                persona=p.persona,
                remaining_pieces=p.remaining_pieces.copy(),
                has_passed=p.has_passed,
                last_piece_was_monomino=p.last_piece_was_monomino,
                status=p.status,
                score=p.score,
                turn_order=p.turn_order
            )
            for p in self.players
        ]
        
        # Create new GameManager with copied players
        new_game_manager = GameManager(new_players, self.current_player_idx)
        new_game_manager.turn_history = self.game_manager.turn_history.copy()
        new_game_manager.game_finished = self.game_manager.game_finished
        
        new_game = Game(
            board=self.board.copy(),
            move_history=self.move_history.copy(),
            status=self.status,
            game_manager=new_game_manager
        )
        
        return new_game
    
    def __repr__(self) -> str:
        return (
            f"Game(players={self.num_players}, "
            f"turn={self.turn_number}, "
            f"current_player={self.current_player_idx}, "
            f"status={self.status.value})"
        )
