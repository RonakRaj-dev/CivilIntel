"""
Vision Threat Detector - Optimized for CPU Inference
Uses PaliGemma 3B Mix to detect safety threats in video frames.
"""

import json
import torch
from PIL import Image
from transformers import PaliGemmaForConditionalGeneration, PaliGemmaProcessor

# Define the categories the model should look for
ALLOWED_CATEGORIES = [
    "physical_violence",
    "weapon_presence",
    "injured_person",
    "harassment",
    "crowd_aggression",
    "fire_or_explosion",
    "accident",
    "non_threat"
]

class VisionThreatDetector:
    """
    Detects safety threats in images using local PaliGemma weights.
    Optimized for systems without a dedicated GPU.
    """

    def __init__(self, model_path: str = "./paligemma-weights"):
        """
        Initialize the detector using local shards.

        Args:
            model_path: Path to the folder containing .safetensors and .json files.
        """
        print(f"🔧 Loading Vision Core from: {model_path}")

        try:
            # use_fast=True silences the 'slow processor' warning
            self.processor = PaliGemmaProcessor.from_pretrained(model_path, use_fast=True)

            # Optimized for CPU: float32 math and memory sharding
            self.model = PaliGemmaForConditionalGeneration.from_pretrained(
                model_path,
                dtype=torch.float32,     # Use 'dtype' instead of deprecated 'torch_dtype'
                device_map="cpu",        # Hard-coded for no-GPU environments
                low_cpu_mem_usage=True,  # Prevents RAM spikes during loading
                local_files_only=True    # Ensures no internet calls are made
            ).eval()                     # Set to evaluation mode to save resources

            self.device = "cpu"
            print(f"✅ Model loaded successfully on {self.device} (Weights: 3/3 Shards)")

        except Exception as e:
            print(f"⚠️ Error loading model: {str(e)}")
            print("💡 Tip: Ensure your 'paligemma-weights' folder contains all .safetensors and .json files.")
            raise

    def analyze(self, image: Image.Image) -> dict:
        """
        Analyze a single image/frame for safety threats.

        Args:
            image: PIL Image object.

        Returns:
            Dictionary with category, confidence, and justification.
        """
        try:
            # Prepare prompt with the required <image> token
            prompt = self._create_prompt()

            # Process inputs for the CPU
            inputs = self.processor(
                text=prompt,
                images=image,
                return_tensors="pt"
            ).to(self.device)

            # Generate response with deterministic settings for audit consistency
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=128,
                    do_sample=False,
                    use_cache=True # Speeds up CPU text generation
                )

            # Decode and clean output
            decoded = self.processor.decode(output[0], skip_special_tokens=True)

            # Remove the prompt prefix from the response
            raw_response = decoded.replace(prompt, "").strip()

            return self._parse_response(raw_response)

        except Exception as e:
            print(f"⚠️ Analysis error: {str(e)}")
            return {
                "category": "non_threat",
                "confidence": 0.0,
                "justification": f"Internal CPU Error: {str(e)}"
            }

    def _create_prompt(self) -> str:
        """Create the analysis prompt with mandatory multimodal tokens"""
        return f"<image>answer en Task: Public Safety Audit. Categorize into ONE: {', '.join(ALLOWED_CATEGORIES)}. Respond ONLY with valid JSON."

    def _parse_response(self, response_text: str) -> dict:
        """
        Parse the model's response into a structured format.
        """
        try:
            # Find JSON boundaries in case the model adds extra text
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                result = json.loads(json_str)
            else:
                raise ValueError("No JSON object found in response")

            # Validate the category
            if result.get("category") not in ALLOWED_CATEGORIES:
                result["category"] = "non_threat"

            return result

        except Exception:
            # Fallback if JSON parsing fails
            return {
                "category": "non_threat",
                "confidence": 0.3,
                "justification": f"Unstructured response: {response_text[:100]}"
            }

# Standalone test logic
if __name__ == "__main__":
    print("=" * 60)
    print("VISION THREAT DETECTOR - TEST MODE")
    print("=" * 60)

    # Create a simple test image (blank white)
    test_image = Image.new('RGB', (224, 224), color='white')

    detector = VisionThreatDetector()
    result = detector.analyze(test_image)

    print("\nTest Results:")
    print(json.dumps(result, indent=2))