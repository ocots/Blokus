"""
Metrics tracking for Blokus RL training.

Supports:
- CSV logging for persistence
- TensorBoard for visualization
- In-memory history for dashboard
"""

import csv
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json


@dataclass
class MetricsSnapshot:
    """Single point in metrics history."""
    step: int
    episode: int
    timestamp: str
    metrics: Dict[str, float]


class MetricsTracker:
    """
    Centralized metrics tracking with CSV and TensorBoard support.
    
    Metrics are organized by category:
    - train/: Training metrics (loss, q_value, etc.)
    - eval/: Evaluation metrics (win_rate, score_diff, etc.)
    - env/: Environment metrics (steps, reward, etc.)
    - system/: System metrics (eps_per_sec, memory, etc.)
    """
    
    def __init__(
        self,
        log_dir: Path,
        use_tensorboard: bool = True,
        csv_filename: str = "metrics.csv"
    ):
        """
        Initialize metrics tracker.
        
        Args:
            log_dir: Directory for logs
            use_tensorboard: Enable TensorBoard logging
            csv_filename: Name of CSV file for metrics
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.csv_path = self.log_dir / csv_filename
        self.use_tensorboard = use_tensorboard
        
        # TensorBoard writer
        self._writer = None
        if use_tensorboard:
            try:
                from torch.utils.tensorboard import SummaryWriter
                self._writer = SummaryWriter(str(self.log_dir / "tensorboard"))
            except ImportError:
                print("Warning: TensorBoard not available, disabling")
                self.use_tensorboard = False
        
        # In-memory history (recent entries)
        self.history: List[MetricsSnapshot] = []
        self.max_history_size = 10000
        
        # CSV header tracking
        self._csv_columns: Optional[List[str]] = None
        self._init_csv()
    
    def _init_csv(self) -> None:
        """Initialize CSV file if it exists, load columns."""
        if self.csv_path.exists():
            with open(self.csv_path, "r") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header:
                    self._csv_columns = header
    
    def log(
        self,
        step: int,
        episode: int,
        metrics: Dict[str, float]
    ) -> None:
        """
        Log metrics for a training step.
        
        Args:
            step: Global step number
            episode: Episode number
            metrics: Dict of metric_name -> value
        """
        timestamp = datetime.now().isoformat()
        
        # Add to history
        snapshot = MetricsSnapshot(
            step=step,
            episode=episode,
            timestamp=timestamp,
            metrics=metrics.copy()
        )
        self.history.append(snapshot)
        
        # Trim history if too large
        if len(self.history) > self.max_history_size:
            self.history = self.history[-self.max_history_size // 2:]
        
        # Log to TensorBoard
        if self._writer is not None:
            for key, value in metrics.items():
                self._writer.add_scalar(key, value, step)
        
        # Log to CSV
        self._append_csv(step, episode, timestamp, metrics)
    
    def _append_csv(
        self,
        step: int,
        episode: int,
        timestamp: str,
        metrics: Dict[str, float]
    ) -> None:
        """Append a row to CSV file."""
        # Build row data
        row_data = {
            "step": step,
            "episode": episode,
            "timestamp": timestamp,
            **metrics
        }
        
        # Check if we need to write header
        all_columns = ["step", "episode", "timestamp"] + sorted(metrics.keys())
        
        if self._csv_columns is None:
            # First write - create header
            self._csv_columns = all_columns
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self._csv_columns)
                writer.writeheader()
                writer.writerow(row_data)
        else:
            # Check for new columns
            new_columns = [c for c in all_columns if c not in self._csv_columns]
            
            if new_columns:
                # Need to rewrite CSV with new columns
                self._csv_columns = self._csv_columns + new_columns
                self._rewrite_csv_with_new_columns()
            
            # Append row
            with open(self.csv_path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self._csv_columns)
                writer.writerow(row_data)
    
    def _rewrite_csv_with_new_columns(self) -> None:
        """Rewrite CSV file with new columns (adds empty values for old rows)."""
        # Read existing data
        rows = []
        if self.csv_path.exists():
            with open(self.csv_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        
        # Rewrite with updated columns
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self._csv_columns)
            writer.writeheader()
            writer.writerows(rows)
    
    def log_eval(self, step: int, episode: int, eval_results) -> None:
        """
        Log evaluation results.
        
        Args:
            step: Global step
            episode: Episode number
            eval_results: EvalResults object
        """
        metrics = {
            "eval/win_rate": eval_results.win_rate,
            "eval/avg_score_diff": eval_results.avg_score_diff,
            "eval/avg_steps": eval_results.avg_steps,
            "eval/wins": eval_results.wins,
            "eval/losses": eval_results.losses,
        }
        self.log(step, episode, metrics)
    
    def get_latest(self, n: int = 100) -> List[MetricsSnapshot]:
        """Get latest N metrics snapshots."""
        return self.history[-n:]
    
    def get_metric_history(self, metric_name: str) -> List[tuple]:
        """
        Get history for a specific metric.
        
        Returns:
            List of (step, value) tuples
        """
        result = []
        for snapshot in self.history:
            if metric_name in snapshot.metrics:
                result.append((snapshot.step, snapshot.metrics[metric_name]))
        return result
    
    def flush(self) -> None:
        """Flush TensorBoard writer."""
        if self._writer is not None:
            self._writer.flush()
    
    def close(self) -> None:
        """Close all resources."""
        if self._writer is not None:
            self._writer.close()
            self._writer = None
    
    @classmethod
    def load_from_csv(cls, csv_path: Path) -> "MetricsTracker":
        """
        Load metrics from an existing CSV file.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            MetricsTracker with loaded history
        """
        tracker = cls(
            log_dir=csv_path.parent,
            use_tensorboard=False,
            csv_filename=csv_path.name
        )
        
        if csv_path.exists():
            with open(csv_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    step = int(row.get("step", 0))
                    episode = int(row.get("episode", 0))
                    timestamp = row.get("timestamp", "")
                    
                    metrics = {}
                    for key, value in row.items():
                        if key not in ["step", "episode", "timestamp"]:
                            try:
                                metrics[key] = float(value)
                            except (ValueError, TypeError):
                                pass
                    
                    tracker.history.append(MetricsSnapshot(
                        step=step,
                        episode=episode,
                        timestamp=timestamp,
                        metrics=metrics
                    ))
        
        return tracker
