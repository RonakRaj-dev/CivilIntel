"""
Video Safety Engine - Optimized for CPU Inference
Analyzes videos by sampling keyframes to manage computational load.
"""

import cv2
from PIL import Image
import numpy as np
from typing import Dict, List, Any
from datetime import timedelta
from pathlib import Path

# Import your local optimized detector
from vision_threat_detection import VisionThreatDetector

class VideoSafetyEngine:
    """
    Analyzes video files for safety threats with CPU-specific optimizations.
    """

    def __init__(
            self,
            # Pointing to your local weights folder by default
            model_path: str = "./paligemma-weights",
            # Analyze every 2 seconds for a standard 30fps video
            frame_interval: int = 60,
            confidence_threshold: float = 0.5
    ):
        """
        Initialize the engine with local CPU-optimized weights.
        """
        # Load the detector using your local path
        self.detector = VisionThreatDetector(model_path=model_path)
        self.frame_interval = frame_interval
        self.confidence_threshold = confidence_threshold

    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """
        Extracts and analyzes frames from video at intervals.
        """
        video_path = Path(video_path)
        if not video_path.exists():
            return {"error": "Video file not found", "threat_detected": False}

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return {"error": "Cannot open video file", "threat_detected": False}

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_sec = total_frames / fps if fps > 0 else 0

        # Dynamic interval adjustment: ensure we analyze at least 1 frame every 2 seconds
        actual_interval = max(self.frame_interval, int(fps * 2))

        print(f"📹 Video Info: {duration_sec:.2f}s duration | {fps:.2f} FPS")
        print(f"🔍 CPU Sampling: Analyzing 1 frame every {actual_interval} frames (~every 2s)")

        frame_results = []
        frame_idx = 0
        analyzed_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % actual_interval == 0:
                timestamp = frame_idx / fps if fps > 0 else 0

                # Pre-processing for the detector
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)

                # CPU Analysis: This will take ~30-50s per frame
                print(f"  [Audit] Analyzing frame at {int(timestamp)}s...")
                result = self.detector.analyze(pil_image)

                frame_results.append({
                    "frame_number": frame_idx,
                    "timestamp_sec": round(timestamp, 2),
                    "timestamp_formatted": str(timedelta(seconds=int(timestamp))),
                    **result
                })
                analyzed_count += 1

            frame_idx += 1

        cap.release()
        print(f"✅ Audit Complete: {analyzed_count} keyframes analyzed.")

        summary = self._aggregate_results(frame_results, duration_sec)
        return {
            "video_metadata": {
                "filename": video_path.name,
                "duration": round(duration_sec, 2),
                "frames_sampled": analyzed_count
            },
            "frame_by_frame": frame_results,
            "summary": summary
        }

    def _aggregate_results(self, frame_results: List[Dict], duration_sec: float) -> Dict[str, Any]:
        """Consolidates individual frame scores into a final threat assessment."""
        if not frame_results:
            return {"threat_detected": False, "threat_level": "none"}

        # Filter out non-threats to find the primary danger
        threats = [r for r in frame_results if r["category"] != "non_threat"]

        if not threats:
            return {
                "threat_detected": False,
                "threat_level": "none",
                "message": "No safety violations detected in sampled frames."
            }

        # Calculate average confidence for the most frequent threat category
        categories = [t["category"] for t in threats]
        dominant_category = max(set(categories), key=categories.count)
        avg_conf = np.mean([t["confidence"] for t in threats if t["category"] == dominant_category])

        threat_detected = avg_conf >= self.confidence_threshold

        return {
            "threat_detected": threat_detected,
            "threat_level": "high" if avg_conf > 0.8 else "medium" if avg_conf > 0.5 else "low",
            "dominant_threat": dominant_category,
            "average_confidence": round(float(avg_conf), 3),
            "total_incidents_found": len(threats)
        }