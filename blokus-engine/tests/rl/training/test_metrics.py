import pytest
import csv
from pathlib import Path
import tempfile
from blokus.rl.training.metrics import MetricsTracker, MetricsSnapshot


class TestMetricsTracker:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_init_creates_dir(self, temp_dir):
        """Tracker should create log directory."""
        log_dir = temp_dir / "logs"
        MetricsTracker(log_dir, use_tensorboard=False)
        assert log_dir.exists()

    def test_log_history_and_csv(self, temp_dir):
        """Log should update history and write to CSV."""
        tracker = MetricsTracker(temp_dir, use_tensorboard=False)
        metrics = {"train/loss": 0.5, "env/reward": 10.0}
        tracker.log(step=1, episode=1, metrics=metrics)
        
        # History check
        assert len(tracker.history) == 1
        assert tracker.history[0].step == 1
        assert tracker.history[0].metrics["train/loss"] == 0.5
        
        # CSV check
        assert tracker.csv_path.exists()
        with open(tracker.csv_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert float(rows[0]["train/loss"]) == 0.5
            assert float(rows[0]["env/reward"]) == 10.0

    def test_new_metrics_columns(self, temp_dir):
        """Adding a new metric mid-training should rewrite CSV with new columns."""
        tracker = MetricsTracker(temp_dir, use_tensorboard=False)
        
        # First log
        tracker.log(1, 1, {"a": 1.0})
        with open(tracker.csv_path, "r") as f:
            header = next(csv.reader(f))
            assert "a" in header
            assert "b" not in header
            
        # Second log with new metric
        tracker.log(2, 1, {"a": 2.0, "b": 3.0})
        with open(tracker.csv_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["a"] == "1.0"
            assert rows[0]["b"] == "" # Empty for first row
            assert rows[1]["a"] == "2.0"
            assert rows[1]["b"] == "3.0"

    def test_get_metric_history(self, temp_dir):
        """Should return history for a specific metric."""
        tracker = MetricsTracker(temp_dir, use_tensorboard=False)
        tracker.log(1, 1, {"loss": 0.5})
        tracker.log(2, 1, {"loss": 0.4})
        tracker.log(3, 1, {"other": 1.0})
        
        history = tracker.get_metric_history("loss")
        assert len(history) == 2
        assert history == [(1, 0.5), (2, 0.4)]

    def test_load_from_csv(self, temp_dir):
        """Should load history from existing CSV."""
        csv_path = temp_dir / "old_metrics.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["step", "episode", "timestamp", "loss"])
            writer.writeheader()
            writer.writerow({"step": 1, "episode": 1, "timestamp": "now", "loss": 0.5})
            writer.writerow({"step": 2, "episode": 1, "timestamp": "now", "loss": 0.4})
            
        tracker = MetricsTracker.load_from_csv(csv_path)
        assert len(tracker.history) == 2
        assert tracker.history[0].step == 1
        assert tracker.history[1].metrics["loss"] == 0.4
