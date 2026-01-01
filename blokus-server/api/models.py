from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

# Remirror PieceType if we can't import directly, or use string/enums
# For simplicity, we use strings for PieceType in the API contract
class PieceTypeStr(str, Enum):
    I1 = "I1"
    I2 = "I2"
    I3 = "I3"
    L3 = "L3"
    I4 = "I4"
    L4 = "L4"
    T4 = "T4"
    O4 = "O4"
    S4 = "S4"
    F = "F"
    I5 = "I5"
    L5 = "L5"
    N = "N"
    P = "P"
    T5 = "T5"
    U = "U"
    V = "V"
    W = "W"
    X = "X"
    Y = "Y"
    Z = "Z"

class PlayerState(BaseModel):
    id: int
    pieces_remaining: List[str] # List of PieceType names
    score: int
    has_passed: bool

class GameState(BaseModel):
    board: List[List[int]] # 20x20 grid
    players: List[PlayerState]
    current_player_id: int
    status: str
    turn_number: int

class MoveRequest(BaseModel):
    player_id: int
    piece_type: str
    orientation: int
    row: int
    col: int

class MoveResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    game_state: Optional[GameState] = None

class CreateGameRequest(BaseModel):
    num_players: int = 4

class PlayerConfig(BaseModel):
    name: str
    type: str # 'human', 'ai', 'shared'
    persona: Optional[str] = None # 'random', 'aggressive', 'defensive', etc.

class CreateGameRequest(BaseModel):
    num_players: int = 4
    players: Optional[List[PlayerConfig]] = None

