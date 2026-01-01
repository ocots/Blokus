"""
Tests for training infrastructure.
"""

import pytest
import tempfile
from pathlib import Path
import json

from blokus.rl.training.config import TrainingConfig
from blokus.rl.training.checkpoint import CheckpointManager, TrainingState
from blokus.rl.training.metrics import MetricsTracker
from blokus.rl.training.evaluator import Evaluator, EvalResults
from blokus.rl.agents.random_agent import RandomAgent


class TestTrainingConfig:
    """Tests for TrainingConfig."""
    
    def test_default_config(self):
        """Default config should have sensible values."""
        config = TrainingConfig()
        assert config.board_size == 14
        assert config.num_players == 2
        assert config.eval_frequency == 1000
        assert config.gamma == 0.99
    
    def test_to_dict_roundtrip(self):
        """Config should survive dict conversion."""
        config = TrainingConfig(
            experiment_name="test_exp",
            learning_rate=0.001
        )
        d = config.to_dict()
        restored = TrainingConfig.from_dict(d)
        assert restored.experiment_name == "test_exp"
        assert restored.learning_rate == 0.001


class TestCheckpointManager:
    """Tests for CheckpointManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_create_experiment(self, temp_dir):
        """Should create experiment directory structure."""
        config = TrainingConfig(experiment_name="test")
        manager = CheckpointManager.create_experiment(
            name="test",
            config=config,
            base_dir=temp_dir
        )
        
        assert manager.experiment_dir.exists()
        assert manager.metadata_path.exists()
        assert (manager.experiment_dir / "tensorboard").exists()
    
    def test_save_load_metadata(self, temp_dir):
        """Should save and load metadata correctly."""
        exp_dir = temp_dir / "exp1"
        manager = CheckpointManager(exp_dir)
        
        state = TrainingState(
            experiment_name="test",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
            total_episodes=1000,
            total_steps=50000,
            current_epoch=5,
            best_win_rate=0.75,
            best_epoch=4,
            current_epsilon=0.5,
            config={"lr": 0.001}
        )
        
        manager.save_metadata(state)
        loaded = manager.load_metadata()
        
        assert loaded is not None
        assert loaded.total_episodes == 1000
        assert loaded.best_win_rate == 0.75
    
    def test_list_experiments(self, temp_dir):
        """Should list all experiments."""
        # Create two experiments
        config = TrainingConfig()
        CheckpointManager.create_experiment("exp1", config, temp_dir)
        CheckpointManager.create_experiment("exp2", config, temp_dir)
        
        experiments = CheckpointManager.list_experiments(temp_dir)
        assert len(experiments) == 2


class TestMetricsTracker:
    """Tests for MetricsTracker."""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_log_creates_csv(self, temp_dir):
        """Logging should create CSV file."""
        tracker = MetricsTracker(temp_dir, use_tensorboard=False)
        tracker.log(step=1, episode=1, metrics={"loss": 0.5})
        
        assert tracker.csv_path.exists()
    
    def test_log_appends_to_csv(self, temp_dir):
        """Multiple logs should append to CSV."""
        tracker = MetricsTracker(temp_dir, use_tensorboard=False)
        tracker.log(step=1, episode=1, metrics={"loss": 0.5})
        tracker.log(step=2, episode=2, metrics={"loss": 0.4})
        
        # Read CSV and check
        import csv
        with open(tracker.csv_path) as f:
            rows = list(csv.DictReader(f))
        
        assert len(rows) == 2
        assert float(rows[0]["loss"]) == 0.5
        assert float(rows[1]["loss"]) == 0.4
    
    def test_history_tracking(self, temp_dir):
        """Should maintain in-memory history."""
        tracker = MetricsTracker(temp_dir, use_tensorboard=False)
        
        for i in range(10):
            tracker.log(step=i, episode=i, metrics={"value": i})
        
        history = tracker.get_latest(5)
        assert len(history) == 5
        assert history[-1].metrics["value"] == 9


class TestRandomAgent:
    """Tests for RandomAgent."""
    
    def test_selects_valid_action(self):
        """Should only select valid actions."""
        import numpy as np
        agent = RandomAgent(seed=42)
        
        mask = np.array([False, True, False, True, False])
        action = agent.select_action(
            observation=np.zeros((14, 14, 47)),
            action_mask=mask
        )
        
        assert mask[action] == True
    
    def test_reproducible_with_seed(self):
        """Same seed should give same sequence."""
        import numpy as np
        
        agent1 = RandomAgent(seed=42)
        agent2 = RandomAgent(seed=42)
        
        mask = np.array([True] * 10)
        obs = np.zeros((14, 14, 47))
        
        actions1 = [agent1.select_action(obs, mask) for _ in range(5)]
        actions2 = [agent2.select_action(obs, mask) for _ in range(5)]
        
        assert actions1 == actions2
    
    def test_reset_restores_seed(self):
        """Reset should restore RNG state."""
        import numpy as np
        
        agent = RandomAgent(seed=42)
        mask = np.array([True] * 10)
        obs = np.zeros((14, 14, 47))
        
        actions1 = [agent.select_action(obs, mask) for _ in range(5)]
        agent.reset()
        actions2 = [agent.select_action(obs, mask) for _ in range(5)]
        
        assert actions1 == actions2


class TestEvaluator:
    """Tests for Evaluator."""
    
    def test_evaluate_random_vs_random(self):
        """Two random agents should have ~50% win rate."""
        from blokus.rl import BlokusEnv
        
        def env_factory():
            return BlokusEnv(num_players=2, board_size=14)
        
        evaluator = Evaluator(
            env_factory=env_factory,
            baseline=RandomAgent(seed=42),
            num_games=20,
            swap_sides=True
        )
        
        agent = RandomAgent(seed=123)  # Different seed
        results = evaluator.evaluate(agent)
        
        assert isinstance(results, EvalResults)
        assert results.total_games == 20
        # Win rate should be roughly 50% for random vs random
        # Allow wide margin due to small sample
        assert 0.2 <= results.win_rate <= 0.8
