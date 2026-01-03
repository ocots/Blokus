from pydantic import BaseModel, field_validator
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
    name: str
    color: str
    type: str  # 'human', 'ai'
    persona: Optional[str] = None
    pieces_remaining: List[str]  # List of PieceType names
    pieces_count: int
    squares_remaining: int
    score: int
    has_passed: bool
    status: str  # 'waiting', 'playing', 'passed', 'finished'
    display_name: str
    turn_order: Optional[int] = None

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
    move: Optional[MoveRequest] = None

class PlayerConfig(BaseModel):
    name: str
    type: str # 'human', 'ai'
    persona: Optional[str] = None # 'random', 'aggressive', 'defensive', etc.
    
    @field_validator('type')
    @classmethod
    def validate_player_type(cls, v):
        valid_types = ['human', 'ai']
        if v not in valid_types:
            raise ValueError(f'player type must be one of {valid_types}')
        return v

class CreateGameRequest(BaseModel):
    num_players: int = 4
    players: Optional[List[PlayerConfig]] = None
    start_player: Optional[int] = None
    two_player_mode: Optional[str] = None # 'duo' or 'classic'
    board_size: Optional[int] = None

    
    @field_validator('start_player')
    @classmethod
    def validate_start_player(cls, v, info):
        if v is not None:
            num_players = info.data.get('num_players', 4)
            if v < 0 or v >= num_players:
                raise ValueError(f'start_player must be between 0 and {num_players - 1}')
        return v


class AIModelInfo(BaseModel):
    """Information about an available AI model."""
    id: str
    name: str
    description: str
    level: str
    style: str
    tags: List[str]
    enabled: bool
    tooltip: str
