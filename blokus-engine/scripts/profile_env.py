
import cProfile
import pstats
import io
import gymnasium as gym
import time
import numpy as np
from blokus.rl import BlokusEnv

def run_sample_games(n=5):
    env = BlokusEnv(render_mode=None, board_size=14)
    
    start_time = time.time()
    for i in range(n):
        obs, info = env.reset()
        done = False
        while not done:
            # Get valid action mask (this is likely a major bottleneck)
            mask = env.action_masks()
            
            # Pick a random valid move from the mask
            valid_indices = np.where(mask)[0]
            if len(valid_indices) == 0:
                 # This case is usually handled by the env by forcing a pass
                 # but we'll try to sample anything just to proceed
                 action = 0 
            else:
                action = np.random.choice(valid_indices)
            
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
    
    end_time = time.time()
    print(f"Total time for {n} games: {end_time - start_time:.2f}s")
    print(f"Avg time per game: {(end_time - start_time)/n:.2f}s")

if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()
    run_sample_games(5)
    pr.disable()
    
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(30) # Top 30 functions
    print(s.getvalue())
