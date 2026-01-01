# Agents module
"""RL Agents for Blokus."""

from blokus.rl.agents.base import Agent
from blokus.rl.agents.random_agent import RandomAgent

# DQN requires torch, make import optional
try:
    from blokus.rl.agents.dqn_agent import DQNAgent
    _HAS_TORCH = True
except ImportError:
    DQNAgent = None  # type: ignore
    _HAS_TORCH = False

__all__ = [
    "Agent",
    "RandomAgent",
    "DQNAgent",
]
