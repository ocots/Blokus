"""
Video frame sampler using Reservoir Sampling.

Maintains a fixed-size sample of frames that is uniformly distributed
over all frames seen, regardless of final training duration.
"""

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
import numpy as np


@dataclass
class Frame:
    """A single frame with metadata."""
    image: np.ndarray
    index: int  # Original frame index
    metrics: Dict[str, Any] = field(default_factory=dict)


class VideoFrameSampler:
    """
    Samples frames using Reservoir Sampling for training videos.
    
    Algorithm:
    - Keep the first K frames
    - For each new frame i (i > K):
      - With probability K/i, replace a random existing frame
    
    Result: Uniform sample of K frames over all N frames seen.
    This works even when N is unknown in advance.
    """
    
    def __init__(self, max_frames: int = 100, seed: int = 42):
        """
        Initialize sampler.
        
        Args:
            max_frames: Maximum number of frames to keep
            seed: Random seed for reproducibility
        """
        self.max_frames = max_frames
        self.rng = random.Random(seed)
        
        self.frames: List[Frame] = []
        self.total_seen = 0
        self.enabled = True
    
    def add_frame(
        self,
        image: np.ndarray,
        metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a frame to the sample.
        
        Args:
            image: Frame image (numpy array)
            metrics: Optional metrics to display on frame
            
        Returns:
            True if frame was kept, False if discarded
        """
        if not self.enabled:
            return False
        
        self.total_seen += 1
        
        frame = Frame(
            image=image.copy(),
            index=self.total_seen,
            metrics=metrics or {}
        )
        
        if len(self.frames) < self.max_frames:
            # Still filling up reservoir
            self.frames.append(frame)
            return True
        else:
            # Reservoir sampling
            j = self.rng.randint(0, self.total_seen - 1)
            if j < self.max_frames:
                self.frames[j] = frame
                return True
            return False
    
    def get_sorted_frames(self) -> List[Frame]:
        """Get frames sorted by original index."""
        return sorted(self.frames, key=lambda f: f.index)
    
    def generate_video(
        self,
        output_path: Path,
        fps: int = 10,
        add_overlay: bool = True
    ) -> bool:
        """
        Generate video from sampled frames.
        
        Args:
            output_path: Output video file path
            fps: Frames per second
            add_overlay: Add metrics overlay to frames
            
        Returns:
            True if video was generated successfully
        """
        if len(self.frames) == 0:
            print("No frames to generate video from")
            return False
        
        try:
            import imageio
        except ImportError:
            print("imageio not installed, cannot generate video")
            return False
        
        sorted_frames = self.get_sorted_frames()
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with imageio.get_writer(str(output_path), fps=fps) as writer:
                for frame in sorted_frames:
                    img = frame.image
                    
                    if add_overlay:
                        img = self._add_overlay(img, frame)
                    
                    writer.append_data(img)
            
            print(f"Video saved to {output_path} ({len(sorted_frames)} frames)")
            return True
            
        except Exception as e:
            print(f"Error generating video: {e}")
            return False
    
    def _add_overlay(self, image: np.ndarray, frame: Frame) -> np.ndarray:
        """Add metrics overlay to frame."""
        try:
            import cv2
        except ImportError:
            return image
        
        img = image.copy()
        
        # Add text overlay
        y_offset = 20
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (255, 255, 255)
        thickness = 1
        
        metrics = frame.metrics
        
        # Frame number
        text = f"Frame: {frame.index}"
        cv2.putText(img, text, (10, y_offset), font, font_scale, color, thickness)
        y_offset += 20
        
        # Win rate if available
        if "win_rate" in metrics:
            text = f"Win Rate: {metrics['win_rate']:.1%}"
            cv2.putText(img, text, (10, y_offset), font, font_scale, color, thickness)
            y_offset += 20
        
        # Epoch if available
        if "epoch" in metrics:
            text = f"Epoch: {metrics['epoch']}"
            cv2.putText(img, text, (10, y_offset), font, font_scale, color, thickness)
            y_offset += 20
        
        # Episode if available
        if "episode" in metrics:
            text = f"Episode: {metrics['episode']:,}"
            cv2.putText(img, text, (10, y_offset), font, font_scale, color, thickness)
        
        return img
    
    def clear(self) -> None:
        """Clear all frames."""
        self.frames = []
        self.total_seen = 0
    
    def disable(self) -> None:
        """Disable frame sampling."""
        self.enabled = False
    
    def enable(self) -> None:
        """Enable frame sampling."""
        self.enabled = True
    
    @property
    def num_frames(self) -> int:
        """Number of frames currently stored."""
        return len(self.frames)
    
    def __len__(self) -> int:
        return len(self.frames)
