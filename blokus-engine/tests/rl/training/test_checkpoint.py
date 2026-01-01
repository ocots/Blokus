import pytest
import json
import torch
from pathlib import Path
import tempfile
import shutil
from blokus.rl.training.checkpoint import CheckpointManager, TrainingState, TrainingConfig


class TestCheckpointManager:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def config(self):
        return TrainingConfig(
            experiment_name="test_exp",
            models_dir=Path("tmp_models")
        )

    def test_training_state_serialization(self, config):
        """TrainingState should survive dict roundtrip."""
        state = TrainingState.create_new(config)
        d = state.to_dict()
        restored = TrainingState.from_dict(d)
        assert restored.experiment_name == state.experiment_name
        assert restored.config == state.config

    def test_save_load_metadata(self, temp_dir, config):
        """CheckpointManager should save and load metadata correctly."""
        manager = CheckpointManager(temp_dir)
        state = TrainingState.create_new(config)
        state.total_steps = 123
        
        manager.save_metadata(state)
        assert manager.metadata_path.exists()
        
        loaded = manager.load_metadata()
        assert loaded.total_steps == 123
        assert loaded.experiment_name == config.experiment_name

    def test_save_load_checkpoint(self, temp_dir, config):
        """Should save and load PyTorch model/optimizer states."""
        manager = CheckpointManager(temp_dir)
        state = TrainingState.create_new(config)
        
        # Dummy states
        model_sd = {"weight": torch.tensor([1.0, 2.0])}
        opt_sd = {"lr": 0.001}
        
        # Save
        manager.save_checkpoint(
            state=state,
            model_state_dict=model_sd,
            optimizer_state_dict=opt_sd,
            is_best=True,
            save_periodic=True
        )
        
        assert manager.latest_checkpoint_path.exists()
        assert manager.best_checkpoint_path.exists()
        assert manager.epoch_checkpoint_path(0).exists()
        
        # Load
        checkpoint = manager.load_checkpoint("latest")
        assert checkpoint["epoch"] == 0
        assert torch.equal(checkpoint["model_state_dict"]["weight"], model_sd["weight"])
        
        # Check has_checkpoint
        assert manager.has_checkpoint()

    def test_list_experiments(self, temp_dir, config):
        """Should list all experiments in a directory."""
        # Create two experiments
        CheckpointManager.create_experiment("exp1", config, temp_dir)
        CheckpointManager.create_experiment("exp2", config, temp_dir)
        
        experiments = CheckpointManager.list_experiments(temp_dir)
        assert len(experiments) == 2
        assert any(e.name.startswith("exp1") for e in experiments)
        assert any(e.name.startswith("exp2") for e in experiments)

    def test_list_periodic_checkpoints(self, temp_dir):
        """Should find checkpoint_epoch_X.pt files."""
        manager = CheckpointManager(temp_dir)
        (temp_dir / "checkpoint_epoch_10.pt").touch()
        (temp_dir / "checkpoint_epoch_20.pt").touch()
        (temp_dir / "not_a_checkpoint.pt").touch()
        
        epochs = manager.list_periodic_checkpoints()
        assert epochs == [10, 20]
