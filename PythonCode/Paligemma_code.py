import cv2
import torch
from optimum.intel import OVModelForVisualCausalLM
from transformers import AutoProcessor
from PIL import Image
import time


class VideoSafetyEngine:
    def __init__(self, model_id="google/paligemma-3b-mix-224"):
        print("🔧 Initializing Video Safety Core (CPU Optimized)...")
        self.model = OVModelForVisualCausalLM.from_pretrained(
            model_id, export=True, device="CPU", load_in_8bit=True
        )
        self.processor = AutoProcessor.from_pretrained(model_id)

        # The Master Prompt (same as before, optimized for one-pass detection)
        self.master_prompt = (
            "answer en Task: Video Incident Verification. "
            "Identify: [Weapons, Violence, Fire, Medical Emergency]. "
            "Format: [THREAT: YES/NO] | [SEVERITY 0-10] | [JUSTIFICATION]"
        )

    def analyze_video(self, video_path, sample_fps=1):
        """
        Processes video by sampling 1 frame per second.
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        hop = int(fps / sample_fps) if fps > 0 else 1

        frame_count = 0
        video_results = []

        print(f"🎬 Processing video: {video_path}...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Only analyze every N-th frame to save CPU
            if frame_count % hop == 0:
                # Convert OpenCV BGR to PIL RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)

                # Inference
                inputs = self.processor(text=self.master_prompt, images=pil_img, return_tensors="pt")
                output = self.model.generate(**inputs, max_new_tokens=64)
                analysis = self.processor.decode(output[0], skip_special_tokens=True)

                # Cleanup result (removing prompt from output)
                clean_result = analysis.replace(self.master_prompt, "").strip()
                video_results.append({"frame_sec": round(frame_count / fps, 1), "result": clean_result})

                # Stop early if a catastrophic threat is found (Optional optimization)
                if "SEVERITY 10" in clean_result or "SEVERITY 9" in clean_result:
                    print("⚠️ HIGH SEVERITY DETECTED - BREAKING EARLY")
                    break

            frame_count += 1

        cap.release()
        return self._summarize_video_results(video_results)

    def _summarize_video_results(self, results):
        # A simple logic to find the 'peak' threat in the video
        if not results: return "No frames analyzed."

        # In production, you would parse the 'SEVERITY' numbers to find the max
        return results  # Returns a list of timestamps and their specific findings