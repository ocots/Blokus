"""
Player types and enums for the unified player architecture.

This module defines all the enums and basic types used across the player system.
Follows SOLID principles:
- SRP: Only type definitions
- OCP: Extensible via enum values
"""

from enum import Enum


class PlayerType(Enum):
    """Types of players in the game."""
    HUMAN = "human"
    AI = "ai"


class PlayerStatus(Enum):
    """States of a player during the game."""
    WAITING = "waiting"           # Waiting for their turn
    PLAYING = "playing"           # Currently playing
    PASSED = "passed"             # Has passed their turn
    FINISHED = "finished"         # Game finished for this player


class GameState(Enum):
    """States of the overall game."""
    INITIALIZING = "initializing"
    WAITING_START = "waiting_start"
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"
    ABORTED = "aborted"


class TurnState(Enum):
    """States of a turn."""
    STARTING = "starting"
    SELECTING_PIECE = "selecting_piece"
    PLACING_PIECE = "placing_piece"
    VALIDATING_MOVE = "validating_move"
    EXECUTING_MOVE = "executing_move"
    ENDING = "ending"
    PASSED = "passed"


class MoveState(Enum):
    """States of a move."""
    PROPOSED = "proposed"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    EXECUTED = "executed"
    ANIMATING = "animating"
    COMPLETED = "completed"
    FAILED = "failed"


class UIState(Enum):
    """States of the user interface."""
    IDLE = "idle"
    HOVERING = "hovering"
    DRAGGING = "dragging"
    SELECTING = "selecting"
    ANIMATING = "animating"
    DISABLED = "disabled"
    LOADING = "loading"
