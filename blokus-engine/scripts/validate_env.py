#!/usr/bin/env python3
"""
Validate Blokus RL Environment.

Runs N random episodes to verify the environment works correctly.
Reports statistics on game length, scores, and valid action counts.
"""

import argparse
import numpy as np
import time
from dataclasses import dataclass
from typing import List

from blokus.rl import BlokusEnv


@dataclass
class EpisodeStats:
    """Statistics for a single episode."""
    steps: int
    winner: int | None
    final_scores: List[int]
    mean_valid_actions: float
    total_reward: float


def run_episode(env: BlokusEnv, render: bool = False) -> EpisodeStats:
    """Run a single random episode."""
    obs, info = env.reset()
    done = False
    steps = 0
    total_reward = 0.0
    valid_actions_sum = 0
    
    while not done:
        mask = env.action_masks()
        valid_actions = np.where(mask)[0]
        valid_actions_sum += len(valid_actions)
        
        if len(valid_actions) == 0:
            break
        
        action = np.random.choice(valid_actions)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        done = terminated or truncated
        steps += 1
        
        if render and steps <= 5:
            print(f"Step {steps}: action={action}, reward={reward:.3f}, valid={len(valid_actions)}")
    
    return EpisodeStats(
        steps=steps,
        winner=info.get("winner"),
        final_scores=info.get("scores", []),
        mean_valid_actions=valid_actions_sum / max(steps, 1),
        total_reward=total_reward
    )


def main():
    parser = argparse.ArgumentParser(description="Validate Blokus RL Environment")
    parser.add_argument("-n", "--episodes", type=int, default=100, 
                        help="Number of episodes to run")
    parser.add_argument("--board-size", type=int, default=14,
                        help="Board size (14 for Duo, 20 for Standard)")
    parser.add_argument("--num-players", type=int, default=2,
                        help="Number of players")
    parser.add_argument("--render", action="store_true",
                        help="Render first few steps of each episode")
    parser.add_argument("--shaped-reward", action="store_true", default=True,
                        help="Use shaped reward (default: True)")
    args = parser.parse_args()
    
    print(f"=== Blokus RL Environment Validation ===")
    print(f"Board size: {args.board_size}x{args.board_size}")
    print(f"Players: {args.num_players}")
    print(f"Episodes: {args.episodes}")
    print()
    
    env = BlokusEnv(
        num_players=args.num_players,
        board_size=args.board_size,
        use_shaped_reward=args.shaped_reward
    )
    
    print(f"Observation space: {env.observation_space}")
    print(f"Action space: {env.action_space}")
    print()
    
    start_time = time.time()
    all_stats: List[EpisodeStats] = []
    
    for i in range(args.episodes):
        if args.render:
            print(f"\n--- Episode {i+1} ---")
        stats = run_episode(env, render=args.render)
        all_stats.append(stats)
        
        if (i + 1) % 10 == 0:
            print(f"  Completed {i+1}/{args.episodes} episodes...")
    
    elapsed = time.time() - start_time
    
    # Aggregate statistics
    steps_arr = [s.steps for s in all_stats]
    rewards_arr = [s.total_reward for s in all_stats]
    valid_actions_arr = [s.mean_valid_actions for s in all_stats]
    
    winners = [s.winner for s in all_stats if s.winner is not None]
    winner_counts = {}
    for w in winners:
        winner_counts[w] = winner_counts.get(w, 0) + 1
    
    print()
    print("=== Results ===")
    print(f"Episodes completed: {args.episodes}")
    print(f"Total time: {elapsed:.2f}s ({args.episodes/elapsed:.1f} eps/s)")
    print()
    print(f"Steps:  mean={np.mean(steps_arr):.1f}, min={min(steps_arr)}, max={max(steps_arr)}")
    print(f"Reward: mean={np.mean(rewards_arr):.3f}, min={min(rewards_arr):.3f}, max={max(rewards_arr):.3f}")
    print(f"Valid actions (avg per step): mean={np.mean(valid_actions_arr):.1f}")
    print()
    print(f"Winner distribution: {winner_counts}")
    
    # Sample final scores
    print()
    print("Sample final scores (last 5 episodes):")
    for i, stats in enumerate(all_stats[-5:]):
        print(f"  Episode {args.episodes - 5 + i + 1}: {stats.final_scores}, winner={stats.winner}")
    
    print()
    print("✅ Validation complete!")


if __name__ == "__main__":
    main()
