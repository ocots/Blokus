"""
Training configuration for Blokus RL.
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class TrainingConfig:
    """Configuration for RL training."""
    
    # Experiment
    experiment_name: str = "blokus_experiment"
    
    # Environment
    board_size: int = 14  # 14 for Duo, 20 for Standard
    num_players: int = 2
    
    # Training hyperparameters
    total_episodes: int = 100_000
    learning_rate: float = 1e-4
    batch_size: int = 64
    gamma: float = 0.99  # Discount factor
    
    # Exploration
    epsilon_start: float = 1.0
    epsilon_end: float = 0.05
    epsilon_decay_episodes: int = 50_000
    
    # Memory
    replay_buffer_size: int = 100_000
    min_buffer_size: int = 10_000  # Start training after this many samples
    
    # Evaluation
    eval_frequency: int = 1000  # Evaluate every N episodes
    eval_games: int = 100  # Number of games per evaluation
    
    # Checkpointing
    checkpoint_frequency: int = 10  # Save checkpoint every N epochs
    keep_periodic_checkpoints: bool = True  # Keep checkpoints every N epochs
    
    # Visualization
    use_tensorboard: bool = True
    record_video: bool = True
    max_video_frames: int = 100
    
    # Paths
    models_dir: Path = field(default_factory=lambda: Path("models/experiments"))
    
    def get_experiment_dir(self) -> Path:
        """Get the directory for this experiment."""
        return self.models_dir / self.experiment_name
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "experiment_name": self.experiment_name,
            "board_size": self.board_size,
            "num_players": self.num_players,
            "total_episodes": self.total_episodes,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "gamma": self.gamma,
            "epsilon_start": self.epsilon_start,
            "epsilon_end": self.epsilon_end,
            "epsilon_decay_episodes": self.epsilon_decay_episodes,
            "replay_buffer_size": self.replay_buffer_size,
            "min_buffer_size": self.min_buffer_size,
            "eval_frequency": self.eval_frequency,
            "eval_games": self.eval_games,
            "checkpoint_frequency": self.checkpoint_frequency,
            "keep_periodic_checkpoints": self.keep_periodic_checkpoints,
            "use_tensorboard": self.use_tensorboard,
            "record_video": self.record_video,
            "max_video_frames": self.max_video_frames,
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> "TrainingConfig":
        """Create from dictionary."""
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
