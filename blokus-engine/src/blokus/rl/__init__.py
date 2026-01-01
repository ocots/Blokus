# Blokus RL Module
"""
Reinforcement Learning components for Blokus.

This module provides:
- BlokusEnv: Gym-compatible environment (requires gymnasium)
- Observation tensor creation (47 channels)
- Action space encoding/decoding with masking
- Reward shaping functions
"""

from blokus.rl.observations import create_observation
from blokus.rl.actions import encode_action, decode_action, get_action_mask
from blokus.rl.rewards import potential, shaped_reward

# BlokusEnv requires gymnasium, make import optional
try:
    from blokus.rl.environment import BlokusEnv
    _HAS_GYM = True
except ImportError:
    BlokusEnv = None  # type: ignore
    _HAS_GYM = False

__all__ = [
    "BlokusEnv",
    "create_observation",
    "encode_action",
    "decode_action", 
    "get_action_mask",
    "potential",
    "shaped_reward",
]
