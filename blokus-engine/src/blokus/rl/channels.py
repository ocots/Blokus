"""
Definition of observation channels for Reinforcement Learning.
"""

from enum import IntEnum

class ObservationChannel(IntEnum):
    """
    Indices for the 47-channel observation tensor.
    
    Structure:
    - 0-3: Player occupancy (board state)
    - 4-7: Valid corners (where players can play)
    - 8-11: History T-1 (previous state)
    - 12-15: History T-2 (state before previous)
    - 16: Turn number (normalized)
    - 17-37: Available pieces for current player (one channel per piece type)
    - 38-41: Piece counts for all players (normalized)
    - 42-45: First move flags (is it the first move for player X?)
    - 46: Current player ID (normalized)
    """
    
    # --- Board State (0-3) ---
    PLAYER_1_OCCUPANCY = 0
    PLAYER_2_OCCUPANCY = 1
    PLAYER_3_OCCUPANCY = 2
    PLAYER_4_OCCUPANCY = 3
    
    # --- Valid Corners (4-7) ---
    PLAYER_1_CORNERS = 4
    PLAYER_2_CORNERS = 5
    PLAYER_3_CORNERS = 6
    PLAYER_4_CORNERS = 7
    
    # --- History T-1 (8-11) ---
    HISTORY_T1_PLAYER_1 = 8
    HISTORY_T1_PLAYER_2 = 9
    HISTORY_T1_PLAYER_3 = 10
    HISTORY_T1_PLAYER_4 = 11
    
    # --- History T-2 (12-15) ---
    HISTORY_T2_PLAYER_1 = 12
    HISTORY_T2_PLAYER_2 = 13
    HISTORY_T2_PLAYER_3 = 14
    HISTORY_T2_PLAYER_4 = 15
    
    # --- Game Info (16) ---
    TURN_NUMBER = 16
    
    # --- Available Pieces (17-37) ---
    # Starts at 17, ends at 37 (inclusive)
    # Order follows PieceType enum
    AVAILABLE_PIECES_START = 17
    AVAILABLE_PIECES_END = 37
    
    # --- Piece Counts (38-41) ---
    PLAYER_1_PIECE_COUNT = 38
    PLAYER_2_PIECE_COUNT = 39
    PLAYER_3_PIECE_COUNT = 40
    PLAYER_4_PIECE_COUNT = 41
    
    # --- Flags (42-45) ---
    PLAYER_1_FIRST_MOVE = 42
    PLAYER_2_FIRST_MOVE = 43
    PLAYER_3_FIRST_MOVE = 44
    PLAYER_4_FIRST_MOVE = 45
    
    # --- Current Player (46) ---
    CURRENT_PLAYER_ID = 46

# Total number of channels
NUM_CHANNELS = 47
