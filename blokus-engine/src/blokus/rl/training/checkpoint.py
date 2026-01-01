"""
Checkpoint management for Blokus RL training.

Handles saving and loading of:
- Training state metadata (JSON)
- Model weights (PyTorch .pt)
- Optimizer state
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Any, Dict
import shutil

from blokus.rl.training.config import TrainingConfig


@dataclass
class TrainingState:
    """Complete training state (metadata only, no tensors)."""
    
    # Experiment info
    experiment_name: str
    created_at: str  # ISO format
    updated_at: str  # ISO format
    
    # Progress
    total_episodes: int
    total_steps: int
    current_epoch: int
    
    # Performance
    best_win_rate: float
    best_epoch: int
    current_epsilon: float
    
    # Configuration
    config: Dict[str, Any]
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: dict) -> "TrainingState":
        """Create from dict."""
        return cls(**d)
    
    @classmethod
    def create_new(cls, config: TrainingConfig) -> "TrainingState":
        """Create a fresh training state."""
        now = datetime.now().isoformat()
        return cls(
            experiment_name=config.experiment_name,
            created_at=now,
            updated_at=now,
            total_episodes=0,
            total_steps=0,
            current_epoch=0,
            best_win_rate=0.0,
            best_epoch=0,
            current_epsilon=config.epsilon_start,
            config=config.to_dict()
        )


@dataclass
class ExperimentInfo:
    """Summary info about an experiment."""
    name: str
    path: Path
    created_at: str
    updated_at: str
    total_episodes: int
    best_win_rate: float
    current_epoch: int


class CheckpointManager:
    """
    Manages checkpoints for an experiment.
    
    Directory structure:
        experiment_dir/
        ├── metadata.json           # TrainingState
        ├── checkpoint_latest.pt    # Latest model + optimizer
        ├── checkpoint_best.pt      # Best win rate model
        ├── checkpoint_epoch_10.pt  # Periodic checkpoint
        ├── checkpoint_epoch_20.pt
        ├── metrics.csv             # Training metrics
        └── tensorboard/            # TensorBoard logs
    """
    
    METADATA_FILE = "metadata.json"
    LATEST_CHECKPOINT = "checkpoint_latest.pt"
    BEST_CHECKPOINT = "checkpoint_best.pt"
    
    def __init__(self, experiment_dir: Path):
        """
        Initialize checkpoint manager.
        
        Args:
            experiment_dir: Directory for this experiment
        """
        self.experiment_dir = Path(experiment_dir)
        self.experiment_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def metadata_path(self) -> Path:
        return self.experiment_dir / self.METADATA_FILE
    
    @property
    def latest_checkpoint_path(self) -> Path:
        return self.experiment_dir / self.LATEST_CHECKPOINT
    
    @property
    def best_checkpoint_path(self) -> Path:
        return self.experiment_dir / self.BEST_CHECKPOINT
    
    def epoch_checkpoint_path(self, epoch: int) -> Path:
        return self.experiment_dir / f"checkpoint_epoch_{epoch}.pt"
    
    def save_metadata(self, state: TrainingState) -> None:
        """Save training state metadata to JSON."""
        state.updated_at = datetime.now().isoformat()
        with open(self.metadata_path, "w") as f:
            json.dump(state.to_dict(), f, indent=2)
    
    def load_metadata(self) -> Optional[TrainingState]:
        """Load training state metadata from JSON."""
        if not self.metadata_path.exists():
            return None
        with open(self.metadata_path, "r") as f:
            data = json.load(f)
        return TrainingState.from_dict(data)
    
    def save_checkpoint(
        self,
        state: TrainingState,
        model_state_dict: dict,
        optimizer_state_dict: dict,
        is_best: bool = False,
        save_periodic: bool = False
    ) -> None:
        """
        Save a complete checkpoint.
        
        Args:
            state: Training state metadata
            model_state_dict: Model weights (from model.state_dict())
            optimizer_state_dict: Optimizer state (from optimizer.state_dict())
            is_best: If True, also save as best checkpoint
            save_periodic: If True, also save epoch checkpoint
        """
        try:
            import torch
        except ImportError:
            raise ImportError("PyTorch is required for saving checkpoints")
        
        checkpoint = {
            "model_state_dict": model_state_dict,
            "optimizer_state_dict": optimizer_state_dict,
            "epoch": state.current_epoch,
            "total_episodes": state.total_episodes,
            "total_steps": state.total_steps,
        }
        
        # Save latest
        torch.save(checkpoint, self.latest_checkpoint_path)
        
        # Save metadata
        self.save_metadata(state)
        
        # Save best if applicable
        if is_best:
            shutil.copy(self.latest_checkpoint_path, self.best_checkpoint_path)
        
        # Save periodic checkpoint
        if save_periodic:
            epoch_path = self.epoch_checkpoint_path(state.current_epoch)
            shutil.copy(self.latest_checkpoint_path, epoch_path)
    
    def load_checkpoint(self, checkpoint_type: str = "latest") -> Optional[dict]:
        """
        Load a checkpoint.
        
        Args:
            checkpoint_type: "latest", "best", or epoch number
            
        Returns:
            Checkpoint dict with model_state_dict, optimizer_state_dict, etc.
        """
        try:
            import torch
        except ImportError:
            raise ImportError("PyTorch is required for loading checkpoints")
        
        if checkpoint_type == "latest":
            path = self.latest_checkpoint_path
        elif checkpoint_type == "best":
            path = self.best_checkpoint_path
        else:
            # Assume it's an epoch number
            path = self.epoch_checkpoint_path(int(checkpoint_type))
        
        if not path.exists():
            return None
        
        return torch.load(path, map_location="cpu")
    
    def has_checkpoint(self) -> bool:
        """Check if a checkpoint exists."""
        return self.latest_checkpoint_path.exists()
    
    def list_periodic_checkpoints(self) -> List[int]:
        """List all periodic checkpoint epochs."""
        epochs = []
        for path in self.experiment_dir.glob("checkpoint_epoch_*.pt"):
            try:
                epoch = int(path.stem.split("_")[-1])
                epochs.append(epoch)
            except ValueError:
                continue
        return sorted(epochs)
    
    @classmethod
    def create_experiment(
        cls,
        name: str,
        config: TrainingConfig,
        base_dir: Optional[Path] = None
    ) -> "CheckpointManager":
        """
        Create a new experiment.
        
        Args:
            name: Experiment name
            config: Training configuration
            base_dir: Base directory for experiments
            
        Returns:
            CheckpointManager for the new experiment
        """
        if base_dir is None:
            base_dir = config.models_dir
        
        # Add timestamp to name for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_name = f"{name}_{timestamp}"
        
        experiment_dir = Path(base_dir) / full_name
        experiment_dir.mkdir(parents=True, exist_ok=True)
        
        manager = cls(experiment_dir)
        
        # Create initial state
        config.experiment_name = full_name
        state = TrainingState.create_new(config)
        manager.save_metadata(state)
        
        # Create subdirectories
        (experiment_dir / "tensorboard").mkdir(exist_ok=True)
        
        return manager
    
    @classmethod
    def list_experiments(cls, base_dir: Path) -> List[ExperimentInfo]:
        """
        List all experiments in a directory.
        
        Args:
            base_dir: Directory containing experiments
            
        Returns:
            List of ExperimentInfo objects
        """
        experiments = []
        base_dir = Path(base_dir)
        
        if not base_dir.exists():
            return experiments
        
        for exp_dir in base_dir.iterdir():
            if not exp_dir.is_dir():
                continue
            
            metadata_path = exp_dir / cls.METADATA_FILE
            if not metadata_path.exists():
                continue
            
            try:
                with open(metadata_path, "r") as f:
                    data = json.load(f)
                
                experiments.append(ExperimentInfo(
                    name=data.get("experiment_name", exp_dir.name),
                    path=exp_dir,
                    created_at=data.get("created_at", ""),
                    updated_at=data.get("updated_at", ""),
                    total_episodes=data.get("total_episodes", 0),
                    best_win_rate=data.get("best_win_rate", 0.0),
                    current_epoch=data.get("current_epoch", 0)
                ))
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Sort by updated_at descending
        experiments.sort(key=lambda e: e.updated_at, reverse=True)
        return experiments
