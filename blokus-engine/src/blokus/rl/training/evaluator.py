"""
Evaluator for measuring agent performance against baseline.
"""

from dataclasses import dataclass
from typing import Optional, List
import numpy as np

from blokus.rl.agents.base import Agent
from blokus.rl.agents.random_agent import RandomAgent


@dataclass
class EvalResults:
    """Results from evaluation games."""
    win_rate: float
    avg_score_diff: float
    avg_steps: int
    wins: int
    losses: int
    draws: int
    total_games: int
    
    def __repr__(self) -> str:
        return (
            f"EvalResults(win_rate={self.win_rate:.1%}, "
            f"avg_score_diff={self.avg_score_diff:+.1f}, "
            f"wins={self.wins}, losses={self.losses}, draws={self.draws})"
        )


@dataclass
class GameResult:
    """Result of a single evaluation game."""
    agent_won: bool
    agent_score: int
    baseline_score: int
    steps: int
    
    @property
    def score_diff(self) -> int:
        return self.agent_score - self.baseline_score


class Evaluator:
    """
    Evaluates an agent against a baseline (default: RandomAgent).
    
    The agent always plays as player 0, baseline as player 1.
    """
    
    def __init__(
        self,
        env_factory,  # Callable that creates BlokusEnv
        baseline: Optional[Agent] = None,
        num_games: int = 100,
        swap_sides: bool = True
    ):
        """
        Initialize evaluator.
        
        Args:
            env_factory: Callable that creates a fresh environment
            baseline: Baseline agent (default: RandomAgent with seed 42)
            num_games: Number of games per evaluation
            swap_sides: If True, play half games as each player
        """
        self.env_factory = env_factory
        self.baseline = baseline or RandomAgent(seed=42)
        self.num_games = num_games
        self.swap_sides = swap_sides
    
    def evaluate(self, agent: Agent, verbose: bool = False) -> EvalResults:
        """
        Evaluate an agent against baseline.
        
        Args:
            agent: Agent to evaluate
            verbose: Print progress
            
        Returns:
            EvalResults with statistics
        """
        results: List[GameResult] = []
        
        games_per_side = self.num_games // 2 if self.swap_sides else self.num_games
        
        # Agent plays as player 0
        for i in range(games_per_side):
            result = self._play_game(agent, self.baseline, agent_is_player_0=True)
            results.append(result)
            if verbose and (i + 1) % 10 == 0:
                print(f"  Eval game {i + 1}/{games_per_side} (agent=P0)")
        
        # Agent plays as player 1 (swapped)
        if self.swap_sides:
            for i in range(games_per_side):
                result = self._play_game(agent, self.baseline, agent_is_player_0=False)
                results.append(result)
                if verbose and (i + 1) % 10 == 0:
                    print(f"  Eval game {i + 1}/{games_per_side} (agent=P1)")
        
        return self._aggregate_results(results)
    
    def _play_game(
        self,
        agent: Agent,
        baseline: Agent,
        agent_is_player_0: bool
    ) -> GameResult:
        """Play a single evaluation game."""
        env = self.env_factory()
        obs, info = env.reset()
        
        agent.reset()
        baseline.reset()
        
        done = False
        steps = 0
        
        while not done:
            current_player = info.get("current_player", 0)
            action_mask = env.action_masks()
            
            # Determine which agent plays
            if (current_player == 0) == agent_is_player_0:
                action = agent.select_action(obs, action_mask, deterministic=True)
            else:
                action = baseline.select_action(obs, action_mask, deterministic=True)
            
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            steps += 1
        
        # Get final scores
        scores = info.get("scores", [0, 0])
        agent_idx = 0 if agent_is_player_0 else 1
        baseline_idx = 1 if agent_is_player_0 else 0
        
        agent_score = scores[agent_idx]
        baseline_score = scores[baseline_idx]
        
        # Determine winner
        agent_won = agent_score > baseline_score
        
        return GameResult(
            agent_won=agent_won,
            agent_score=agent_score,
            baseline_score=baseline_score,
            steps=steps
        )
    
    def _aggregate_results(self, results: List[GameResult]) -> EvalResults:
        """Aggregate individual game results."""
        wins = sum(1 for r in results if r.agent_won and r.score_diff > 0)
        losses = sum(1 for r in results if not r.agent_won and r.score_diff < 0)
        draws = sum(1 for r in results if r.score_diff == 0)
        
        total = len(results)
        win_rate = wins / total if total > 0 else 0.0
        avg_score_diff = np.mean([r.score_diff for r in results]) if results else 0.0
        avg_steps = int(np.mean([r.steps for r in results])) if results else 0
        
        return EvalResults(
            win_rate=win_rate,
            avg_score_diff=avg_score_diff,
            avg_steps=avg_steps,
            wins=wins,
            losses=losses,
            draws=draws,
            total_games=total
        )
