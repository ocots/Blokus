#!/usr/bin/env python3
"""
Blokus RL Training Script.

Usage:
    # New experiment
    python train.py --new --name duo_master_v1 --board-size 14
    
    # Resume training
    python train.py --resume duo_master_v1
    
    # Resume latest experiment
    python train.py --resume-latest
    
    # Without visualization
    python train.py --resume duo_master_v1 --no-viz
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np

from blokus.rl import BlokusEnv
from blokus.rl.agents.dqn_agent import DQNAgent
from blokus.rl.agents.random_agent import RandomAgent
from blokus.rl.training.config import TrainingConfig
from blokus.rl.training.checkpoint import CheckpointManager, TrainingState
from blokus.rl.training.metrics import MetricsTracker
from blokus.rl.training.evaluator import Evaluator
from blokus.rl.visualization.video_sampler import VideoFrameSampler


def create_env(config: TrainingConfig) -> BlokusEnv:
    """Create environment from config."""
    return BlokusEnv(
        num_players=config.num_players,
        board_size=config.board_size,
        use_shaped_reward=True
    )


def train_episode(
    env: BlokusEnv,
    agent: DQNAgent,
    opponent: RandomAgent,
    update_frequency: int = 4
) -> dict:
    """
    Train one episode of self-play.
    
    Agent plays as player 0, opponent as player 1.
    
    Args:
        update_frequency: Number of agent steps between network updates
    
    Returns:
        Episode stats dict
    """
    obs, info = env.reset()
    done = False
    episode_reward = 0.0
    episode_steps = 0
    agent_steps = 0
    losses = []
    
    agent.train_mode()
    
    while not done:
        current_player = info["current_player"]
        action_mask = env.action_masks()
        
        if current_player == 0:
            # Agent's turn
            action = agent.select_action(obs, action_mask)
            
            # Store current state for learning
            prev_obs = obs.copy()
            prev_mask = action_mask.copy()
            
            # Take action
            next_obs, reward, terminated, truncated, next_info = env.step(action)
            done = terminated or truncated
            
            # Get next action mask
            next_mask = env.action_masks() if not done else np.zeros_like(action_mask)
            
            # Store transition
            agent.store_transition(
                state=prev_obs,
                action=action,
                reward=reward,
                next_state=next_obs,
                done=done,
                action_mask=prev_mask,
                next_action_mask=next_mask
            )
            
            episode_reward += reward
            agent_steps += 1
            
            # Training step (batched)
            if agent_steps % update_frequency == 0:
                metrics = agent.update()
                if "loss" in metrics:
                    losses.append(metrics["loss"])
            
            obs = next_obs
            info = next_info
        else:
            # Opponent's turn
            action = opponent.select_action(obs, action_mask)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        
        episode_steps += 1
    
    # Final update if there are remaining transitions
    if agent_steps % update_frequency != 0:
        metrics = agent.update()
        if "loss" in metrics:
            losses.append(metrics["loss"])
    
    # Decay epsilon after episode
    agent.decay_epsilon()
    
    # Final game result
    scores = info.get("scores", [0, 0])
    agent_won = scores[0] > scores[1]
    
    return {
        "reward": episode_reward,
        "steps": episode_steps,
        "loss": np.mean(losses) if losses else 0.0,
        "won": agent_won,
        "score_diff": scores[0] - scores[1],
        "epsilon": agent.epsilon
    }


def train(
    config: TrainingConfig,
    checkpoint_manager: CheckpointManager,
    resume: bool = False,
    no_viz: bool = False,
    log_freq: int = 100
):
    """Main training loop."""
    print(f"\n{'='*60}")
    print(f"Blokus RL Training")
    print(f"{'='*60}")
    print(f"Experiment: {config.experiment_name}")
    print(f"Board: {config.board_size}x{config.board_size}")
    print(f"Episodes: {config.total_episodes}")
    print(f"Device: auto")
    print(f"Eval Games: {config.eval_games}")
    print(f"Log Freq: {log_freq} episodes")
    print(f"{'='*60}\n")
    
    # Create components
    env = create_env(config)
    agent = DQNAgent(
        board_size=config.board_size,
        learning_rate=config.learning_rate,
        gamma=config.gamma,
        epsilon_start=config.epsilon_start,
        epsilon_end=config.epsilon_end,
        epsilon_decay=config.epsilon_decay_episodes,
        buffer_size=config.replay_buffer_size,
        batch_size=config.batch_size
    )
    opponent = RandomAgent(seed=42)
    
    # Metrics tracker
    metrics_tracker = MetricsTracker(
        log_dir=checkpoint_manager.experiment_dir,
        use_tensorboard=config.use_tensorboard
    )
    
    # Video sampler
    video_sampler = VideoFrameSampler(
        max_frames=config.max_video_frames
    ) if config.record_video and not no_viz else None
    
    # Evaluator
    evaluator = Evaluator(
        env_factory=lambda: create_env(config),
        baseline=RandomAgent(seed=42),
        num_games=config.eval_games,
        swap_sides=True
    )
    
    # Load checkpoint if resuming
    state = checkpoint_manager.load_metadata()
    start_episode = 0
    best_win_rate = 0.0
    
    if resume and state:
        checkpoint = checkpoint_manager.load_checkpoint("latest")
        if checkpoint:
            # Extract model_state_dict from checkpoint wrapper
            # CheckpointManager saves: {"model_state_dict": agent.state_dict(), ...}
            model_state = checkpoint.get("model_state_dict", checkpoint)
            agent.load_state_dict(model_state)
            start_episode = state.total_episodes
            best_win_rate = state.best_win_rate
            print(f"Resumed from episode {start_episode}, best win rate: {best_win_rate:.1%}")
    else:
        state = TrainingState.create_new(config)
    
    # Training loop
    episode_rewards = []
    recent_wins = []
    start_time = time.time()
    
    try:
        for episode in range(start_episode, config.total_episodes):
            # Train one episode
            ep_stats = train_episode(env, agent, opponent)
            
            episode_rewards.append(ep_stats["reward"])
            recent_wins.append(1 if ep_stats["won"] else 0)
            if len(recent_wins) > 100:
                recent_wins.pop(0)
            
            # Log metrics
            metrics_tracker.log(
                step=agent.steps_done,
                episode=episode,
                metrics={
                    "train/loss": ep_stats["loss"],
                    "train/epsilon": ep_stats["epsilon"],
                    "env/episode_reward": ep_stats["reward"],
                    "env/episode_length": ep_stats["steps"],
                    "env/score_diff": ep_stats["score_diff"],
                    "env/win_rate_100": np.mean(recent_wins) if recent_wins else 0,
                }
            )
            
            # Progress output
            if (episode + 1) % log_freq == 0:
                elapsed = time.time() - start_time
                count = episode - start_episode + 1
                if elapsed > 0:
                    speed = count / elapsed
                    if speed < 1.0:
                        speed_str = f"{1/speed:.2f} s/ep"
                    else:
                        speed_str = f"{speed:.2f} ep/s"
                else:
                    speed_str = "Inf ep/s"
                    
                print(f"Episode {episode + 1}/{config.total_episodes} | "
                      f"Win Rate (100): {np.mean(recent_wins):.1%} | "
                      f"Loss: {ep_stats['loss']:.4f} | "
                      f"Eps: {ep_stats['epsilon']:.3f} | "
                      f"Speed: {speed_str}")
            
            # Evaluation
            if (episode + 1) % config.eval_frequency == 0:
                print(f"\nEvaluating at episode {episode + 1}...")
                agent.eval_mode()
                eval_results = evaluator.evaluate(agent)
                agent.train_mode()
                
                metrics_tracker.log_eval(agent.steps_done, episode, eval_results)
                
                print(f"  Win Rate: {eval_results.win_rate:.1%} | "
                      f"Avg Score Diff: {eval_results.avg_score_diff:+.1f}\n")
                
                # Check if best
                is_best = eval_results.win_rate > best_win_rate
                if is_best:
                    best_win_rate = eval_results.win_rate
                    print(f"  New best! Win rate: {best_win_rate:.1%}")
                
                # Update state
                state.total_episodes = episode + 1
                state.total_steps = agent.steps_done
                state.current_epoch = (episode + 1) // config.eval_frequency
                state.best_win_rate = best_win_rate
                state.current_epsilon = agent.epsilon
                if is_best:
                    state.best_epoch = state.current_epoch
                
                # Checkpoint
                save_periodic = (
                    config.keep_periodic_checkpoints and
                    state.current_epoch % config.checkpoint_frequency == 0
                )
                checkpoint_manager.save_checkpoint(
                    state=state,
                    model_state_dict=agent.state_dict(),
                    optimizer_state_dict={},  # Included in agent state
                    is_best=is_best,
                    save_periodic=save_periodic
                )
                
                # Video frame
                if video_sampler and not no_viz:
                    # Capture a sample frame (simplified - could be board image)
                    video_sampler.add_frame(
                        image=np.zeros((200, 200, 3), dtype=np.uint8),  # Placeholder
                        metrics={
                            "win_rate": eval_results.win_rate,
                            "epoch": state.current_epoch,
                            "episode": episode + 1
                        }
                    )
    
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
    
    finally:
        # Final save
        state.total_episodes = episode + 1 if 'episode' in dir() else start_episode
        state.total_steps = agent.steps_done
        checkpoint_manager.save_checkpoint(
            state=state,
            model_state_dict=agent.state_dict(),
            optimizer_state_dict={},
            is_best=False,
            save_periodic=False
        )
        
        metrics_tracker.flush()
        metrics_tracker.close()
        
        # Generate video
        if video_sampler and len(video_sampler) > 0:
            video_path = checkpoint_manager.experiment_dir / "training_progress.mp4"
            video_sampler.generate_video(video_path)
        
        print(f"\nTraining complete!")
        print(f"Final win rate: {best_win_rate:.1%}")
        print(f"Checkpoint saved to: {config.get_experiment_dir()}")
        print(f"EXPERIMENT_DIR={config.get_experiment_dir()}")  # For CI to capture


def main():
    parser = argparse.ArgumentParser(
        description="Blokus RL Training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Experiment selection
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--new", action="store_true",
                       help="Start new experiment")
    group.add_argument("--resume", type=str, metavar="NAME",
                       help="Resume experiment by name")
    group.add_argument("--resume-latest", action="store_true",
                       help="Resume most recent experiment")
    
    # New experiment options
    parser.add_argument("--name", type=str, default="blokus",
                        help="Experiment name (for --new)")
    parser.add_argument("--board-size", type=int, default=14, choices=[14, 20],
                        help="Board size: 14 for Duo, 20 for Standard")
    parser.add_argument("--episodes", type=int, default=100000,
                        help="Total training episodes")
    
    # Training options
    parser.add_argument("--lr", type=float, default=1e-4,
                        help="Learning rate")
    parser.add_argument("--batch-size", type=int, default=64,
                        help="Batch size")
    parser.add_argument("--epsilon-decay", type=int, default=50000,
                        help="Epsilon decay episodes")
    parser.add_argument("--eval-freq", type=int, default=1000,
                        help="Evaluation frequency (episodes)")
    parser.add_argument("--eval-games", type=int, default=100,
                        help="Number of games per evaluation")
    parser.add_argument("--min-buffer", type=int, default=10000,
                        help="Minimum buffer size before training")
    parser.add_argument("--log-freq", type=int, default=100,
                        help="Logging frequency (episodes)")
    
    # Visualization
    parser.add_argument("--no-viz", action="store_true",
                        help="Disable visualization (TensorBoard, video)")
    parser.add_argument("--no-video", action="store_true",
                        help="Disable video recording")
    
    args = parser.parse_args()
    
    # Models directory
    models_dir = Path(__file__).parent.parent / "models" / "experiments"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    if args.new:
        # Create new experiment
        config = TrainingConfig(
            experiment_name=args.name,
            board_size=args.board_size,
            num_players=2,
            total_episodes=args.episodes,
            learning_rate=args.lr,
            batch_size=args.batch_size,
            epsilon_decay_episodes=args.epsilon_decay,
            eval_frequency=args.eval_freq,
            eval_games=args.eval_games,
            min_buffer_size=args.min_buffer,
            use_tensorboard=not args.no_viz,
            record_video=not args.no_video and not args.no_viz,
            models_dir=models_dir
        )
        # Store log_freq in config or pass it separately? 
        # Since config is frozen/dataclass, easier to pass it or hack it. 
        # But wait, config structure is fixed. Let's pass it to train() function.
        
        checkpoint_manager = CheckpointManager.create_experiment(
            name=args.name,
            config=config,
            base_dir=models_dir
        )
        
        train(config, checkpoint_manager, resume=False, no_viz=args.no_viz, log_freq=args.log_freq)
    
    elif args.resume:
        # Find experiment by name
        experiments = CheckpointManager.list_experiments(models_dir)
        matches = [e for e in experiments if args.resume in e.name]
        
        if not matches:
            print(f"Error: No experiment found matching '{args.resume}'")
            print(f"Available: {[e.name for e in experiments]}")
            sys.exit(1)
        
        exp = matches[0]
        checkpoint_manager = CheckpointManager(exp.path)
        state = checkpoint_manager.load_metadata()
        config = TrainingConfig.from_dict(state.config)
        
        train(config, checkpoint_manager, resume=True, no_viz=args.no_viz, log_freq=args.log_freq)
    
    elif args.resume_latest:
        experiments = CheckpointManager.list_experiments(models_dir)
        if not experiments:
            print("Error: No experiments found")
            sys.exit(1)
        
        exp = experiments[0]  # Already sorted by date
        checkpoint_manager = CheckpointManager(exp.path)
        state = checkpoint_manager.load_metadata()
        config = TrainingConfig.from_dict(state.config)
        
        train(config, checkpoint_manager, resume=True, no_viz=args.no_viz, log_freq=args.log_freq)


if __name__ == "__main__":
    main()
