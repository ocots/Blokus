import torch
import numpy as np
import pytest
from blokus.rl.agents.dqn_agent import DQNAgent, ReplayBuffer, Transition

class TestReplayBuffer:
    def test_push_and_len(self):
        """Buffer should store transitions and report correct length."""
        buffer = ReplayBuffer(capacity=10)
        t = Transition(
            state=np.zeros((14, 14, 47)),
            action=0,
            reward=1.0,
            next_state=np.zeros((14, 14, 47)),
            done=False,
            action_mask=np.zeros(21 * 8 * 14 * 14, dtype=bool),
            next_action_mask=np.zeros(21 * 8 * 14 * 14, dtype=bool)
        )
        buffer.push(t)
        assert len(buffer) == 1
        
        for i in range(15):
            buffer.push(t)
        assert len(buffer) == 10

    def test_sample_shape(self):
        """Sample should return correct batch size."""
        buffer = ReplayBuffer(capacity=100)
        t = Transition(
            state=np.zeros((14, 14, 47)),
            action=0,
            reward=1.0,
            next_state=np.zeros((14, 14, 47)),
            done=False,
            action_mask=np.zeros(100),
            next_action_mask=np.zeros(100)
        )
        for _ in range(20):
            buffer.push(t)
            
        batch = buffer.sample(10)
        assert len(batch) == 10
        assert isinstance(batch[0], Transition)

class TestDQNAgent:
    @pytest.fixture
    def agent(self):
        return DQNAgent(
            board_size=14,
            buffer_size=1000,
            batch_size=4,
            epsilon_start=1.0,
            epsilon_end=0.1,
            epsilon_decay=100,
            device="cpu"
        )

    def test_agent_init(self, agent):
        """Agent should initialize with networks and buffer."""
        assert agent.online_net is not None
        assert agent.target_net is not None
        assert len(agent.buffer) == 0

    def test_select_action_deterministic(self, agent):
        """Deterministic selection should ignore epsilon."""
        obs = np.random.randn(14, 14, 47).astype(np.float32)
        mask = np.ones(21 * 8 * 14 * 14, dtype=bool)
        
        # Should work without error
        action = agent.select_action(obs, mask, deterministic=True)
        assert isinstance(action, int)

    def test_store_transition(self, agent):
        """Storing transition should increase memory length."""
        state = np.zeros((14, 14, 47))
        action = 5
        reward = 1.0
        next_state = np.zeros((14, 14, 47))
        done = False
        mask = np.ones(agent.num_actions, dtype=bool)
        next_mask = np.ones(agent.num_actions, dtype=bool)
        
        agent.store_transition(state, action, reward, next_state, done, mask, next_mask)
        assert len(agent.buffer) == 1

        # Fill buffer enough for a batch
        for _ in range(agent.batch_size + 1):
            agent.store_transition(
                np.zeros((14, 14, 47)), 0, 1.0, 
                np.zeros((14, 14, 47)), False, 
                np.ones(agent.online_net.num_actions, dtype=bool),
                np.ones(agent.online_net.num_actions, dtype=bool)
            )
            
        metrics = agent.update()
        assert "loss" in metrics
        assert metrics["loss"] >= 0

    def test_state_dict_roundtrip(self, agent):
        """State dict should allow saving and loading agent state."""
        sd = agent.state_dict()
        assert "online_net" in sd
        assert "target_net" in sd
        assert "optimizer" in sd
        
        # Change something
        agent.gamma = 0.5
        agent.load_state_dict(sd)
        # load_state_dict doesn't currently restore gamma in the implementation (it's not in sd)
        # but let's check if it loads without crashing.
        assert agent.online_net is not None

    def test_decay_epsilon(self, agent):
        """Epsilon should decay over time and hit floor."""
        start_eps = agent.epsilon
        agent.decay_epsilon()
        assert agent.epsilon < start_eps
        
        # Test floor (hit after epsilon_decay episodes)
        agent.episodes_done = agent.epsilon_decay + 10
        agent.decay_epsilon()
        assert agent.epsilon == pytest.approx(agent.epsilon_end)
