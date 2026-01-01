import pytest
import torch
import numpy as np
from pathlib import Path
import tempfile
from blokus.rl.environment import BlokusEnv
from blokus.rl.agents.dqn_agent import DQNAgent
from blokus.rl.training.metrics import MetricsTracker
from blokus.rl.training.checkpoint import CheckpointManager, TrainingState, TrainingConfig

class TestTrainingIntegration:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_mini_training_loop(self, temp_dir):
        """Run 10 steps of a real training loop to check component interaction."""
        # 1. Setup
        board_size = 14
        env = BlokusEnv(num_players=2, board_size=board_size)
        agent = DQNAgent(
            board_size=board_size,
            batch_size=4,
            buffer_size=100,
            epsilon_decay=10,
            device="cpu"
        )
        tracker = MetricsTracker(temp_dir, use_tensorboard=False)
        
        # 2. Loop
        obs, info = env.reset()
        for step in range(15): # More than batch_size to trigger update
            mask = env.action_masks()
            action = agent.select_action(obs, mask)
            
            next_obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            # Store
            agent.store_transition(
                obs, action, reward, next_obs, done, 
                mask, env.action_masks()
            )
            
            # Update
            if len(agent.buffer) >= agent.batch_size:
                metrics = agent.update()
                if metrics:
                    tracker.log(step, 0, metrics)
            
            if done:
                obs, info = env.reset()
            else:
                obs = next_obs
                
        # 3. Assertions
        assert agent.steps_done > 0
        assert len(tracker.history) > 0
        assert tracker.csv_path.exists()
        
        # Verify epsilon decay
        assert agent.episodes_done >= 0 # episodes_done increments in decay_epsilon which we didn't call here
        # Actually decay_epsilon is usually called at end of episode. Let's call it manually.
        agent.decay_epsilon()
        assert agent.epsilon < agent.epsilon_start
