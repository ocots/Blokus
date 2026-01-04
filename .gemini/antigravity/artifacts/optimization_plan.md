# Implementation Plan - Optimization of Blokus Game Engine for RL Training

## Problem Statement
The current RL training speed is approximately 25-30 seconds per episode on GitHub Actions. Profiling reveals that 99% of this time is spent in the game engine's move validation logic, specifically in board scanning functions that recalculate player metadata (occupied cells, available corners, forbidden edges) for every single candidate placement.

## Proposed Solution
A three-phase optimization strategy to reduce training time by at least 10x-50x.

### Phase 1: Metadata Caching (Current)
- **Goal**: Eliminate redundant board scans within a single turn.
- **Mechanism**: Implement a cache for `player_cells`, `player_corners`, and `player_edges` at the `Board` level.
- **Invalidation**: Clear the cache whenever `place_piece` is called.
- **Status**: Implementation started in `src/blokus/board.py`.

### Phase 2: Vectorized Move Validation (Medium term)
- **Goal**: Replace coordinate-based loops with NumPy bitmask operations.
- **Mechanism**:
    - Use 2D boolean arrays for "Valid Connection Points" and "Forbidden Adjacencies".
    - Validate placements using fast matrix intersections.
- **Expected Outcome**: Drastic reduction in loop overhead in `rules.py`.

### Phase 3: Parallel Execution (Future)
- **Goal**: Fully utilize multi-core runners.
- **Action**: Integrate `SubprocVecEnv` to sample multiple games in parallel.

## Tasks

### T1: Implement Caching in Board [IN PROGRESS]
- [x] Add cache attributes to `Board` class.
- [x] Update `get_player_cells` to use cache.
- [x] Update `get_player_corners` to use cache.
- [x] Update `get_player_edges` to use cache.
- [x] Implement automatic cache invalidation on piece placement.

### T2: Verify and Benchmark
- [ ] Run `scripts/profile_env.py` locally to measure speedup.
- [ ] Ensure all existing tests pass (`npm test` equivalent for Python).
- [ ] Run a 20-episode smoke test on CI to verify real-world speedup.

### T3: Refactor Rules for Cache Alignment
- [ ] Ensure `get_valid_placements` in `rules.py` doesn't bypass the cache.
- [ ] Review `decode_action` and `get_action_mask` for similar redundancies.

## Success Criteria
- Average time per episode < 2 seconds (CI environment).
- Training 10,000 episodes completes in < 6 hours.
