import torch
from transformers import PaliGemmaForConditionalGeneration

def check_env():
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Current GPU: {torch.cuda.get_device_name(0)}")
        # Check if we have enough memory for 4-bit PaLI-Gemma (approx 4GB free)
        free_mem = torch.cuda.mem_get_info()[0] / 1024**3
        print(f"Free VRAM: {free_mem:.2f} GB")
        return free_mem > 4.0
    return False

if __name__ == "__main__":
    if check_env():
        print("✅ Environment ready for PaLI-Gemma 3B (Quantized)")
    else:
        print("⚠️ Warning: Low VRAM. You may need to use a smaller model or CPU (very slow).")