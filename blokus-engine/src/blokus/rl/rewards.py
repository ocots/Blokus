"""
Reward shaping for Blokus RL.

Implements potential-based reward shaping to accelerate learning
while preserving optimal policy invariants.

The shaped reward is:
    R_shaped = R_base + gamma * Φ(s') - Φ(s)

Where Φ(s) is the potential function measuring "goodness" of state s.
"""

import numpy as np
from typing import Optional
from blokus.game import Game, Move, GameStatus
from blokus.pieces import PieceType, PIECES


# Discount factor for shaping
GAMMA = 0.99

# Weights for potential function components
WEIGHT_PLACED = 0.5      # Reward for placed squares
WEIGHT_CORNERS = 0.3     # Reward for available corners
WEIGHT_BIG_PIECES = -0.2  # Penalty for remaining big pieces


def potential(game: Game, player_id: int) -> float:
    """
    Calculate state potential for reward shaping.
    
    The potential function combines:
    - Placed squares (positive) - encourages placing pieces
    - Available corners (positive) - encourages maintaining flexibility
    - Big pieces remaining (negative) - discourages hoarding large pieces
    
    Args:
        game: Current game state
        player_id: Player to calculate potential for
    
    Returns:
        Float potential value in range [0, 1]
    """
    player = game.players[player_id]
    
    # Calculate placed squares (out of 89 total)
    remaining_squares = player.squares_remaining
    placed_squares = 89 - remaining_squares
    placed_normalized = placed_squares / 89.0
    
    # Calculate available corners
    corners = _count_valid_corners(game, player_id)
    corners_normalized = min(corners / 50.0, 1.0)  # Cap at 50 corners
    
    # Count remaining big pieces (size >= 4)
    big_pieces_remaining = sum(
        1 for pt in player.remaining_pieces
        if PIECES[pt][0].size >= 4
    )
    big_pieces_normalized = big_pieces_remaining / 12.0  # 12 pieces of size >= 4
    
    # Combine components
    potential_value = (
        WEIGHT_PLACED * placed_normalized +
        WEIGHT_CORNERS * corners_normalized +
        WEIGHT_BIG_PIECES * big_pieces_normalized
    )
    
    return potential_value


def sparse_reward(game: Game, player_id: int) -> float:
    """
    Calculate sparse terminal reward.
    
    Args:
        game: Current game state (should be terminal)
        player_id: Player to calculate reward for
    
    Returns:
        +1 for win, -1 for loss, 0 for tie or non-terminal
    """
    if game.status != GameStatus.FINISHED:
        return 0.0
    
    scores = game.get_scores()
    player_score = scores[player_id]
    max_score = max(scores)
    
    if player_score == max_score:
        # Check for tie
        winners = sum(1 for s in scores if s == max_score)
        if winners > 1:
            return 0.0  # Tie
        return 1.0  # Win
    else:
        return -1.0  # Loss


def shaped_reward(
    game_before: Game,
    move: Move,
    game_after: Game,
    player_id: Optional[int] = None
) -> float:
    """
    Calculate shaped reward for a transition.
    
    R_shaped = R_base + gamma * Φ(s') - Φ(s)
    
    Args:
        game_before: State before action
        move: The action taken
        game_after: State after action
        player_id: Player perspective (default: move's player)
    
    Returns:
        Shaped reward value
    """
    if player_id is None:
        player_id = move.player_id
    
    # Base reward (sparse terminal)
    base_reward = sparse_reward(game_after, player_id)
    
    # Potential-based shaping
    phi_before = potential(game_before, player_id)
    phi_after = potential(game_after, player_id)
    shaping = GAMMA * phi_after - phi_before
    
    return base_reward + shaping


def dense_reward(game: Game, move: Move, player_id: Optional[int] = None) -> float:
    """
    Calculate a simple dense reward for immediate feedback.
    
    This is an alternative to shaped_reward for simpler training setups.
    
    Args:
        game: Game state after move
        move: The move that was played
        player_id: Player perspective (default: move's player)
    
    Returns:
        Reward value based on piece size and position
    """
    if player_id is None:
        player_id = move.player_id
    
    # Reward based on piece size (larger pieces = more reward)
    piece = move.get_piece()
    size_reward = piece.size / 5.0  # Normalize by max piece size
    
    # Terminal bonus/penalty
    terminal_reward = sparse_reward(game, player_id)
    
    return size_reward + terminal_reward * 10.0


def _count_valid_corners(game: Game, player_id: int) -> int:
    """Count the number of valid corner positions for a player."""
    board = game.board
    board_size = board.size
    corners = set()
    
    # If first move, return starting corners count
    if game.is_first_move(player_id):
        return len(list(board.get_starting_corners(player_id)))
    
    # Find all diagonal positions from player's pieces
    for row in range(board_size):
        for col in range(board_size):
            if board.grid[row, col] == player_id + 1:
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < board_size and 0 <= nc < board_size:
                        if board.grid[nr, nc] == 0:
                            # Check no edge contact
                            has_edge = False
                            for edr, edc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                enr, enc = nr + edr, nc + edc
                                if 0 <= enr < board_size and 0 <= enc < board_size:
                                    if board.grid[enr, enc] == player_id + 1:
                                        has_edge = True
                                        break
                            if not has_edge:
                                corners.add((nr, nc))
    
    return len(corners)
