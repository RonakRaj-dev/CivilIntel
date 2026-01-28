import os
from getpass import getpass
from dotenv import load_dotenv
from transformers import AutoConfig
from huggingface_hub import login

# Load .env variables at startup
load_dotenv()

def ensure_hf_token(model_id):
    """
    Load HF token from .env or prompt if missing.
    Validate access to gated model.
    """

    token = os.getenv("HF_TOKEN")

    if token:
        try:
            AutoConfig.from_pretrained(model_id, token=token)
            print("✔ Hugging Face token loaded from .env and validated.")
            return token
        except Exception:
            print("⚠ HF_TOKEN found but invalid or no access.")

    print("\n🔐 Hugging Face authentication required.")
    token = getpass("Enter Hugging Face token (input hidden): ")

    try:
        login(token=token)
        AutoConfig.from_pretrained(model_id, token=token)
        os.environ["HF_TOKEN"] = token
        print("✔ Token accepted and access verified.\n")
        return token

    except Exception as e:
        print("\n❌ Token validation failed.")
        print("Reason:", str(e))
        raise SystemExit(1)
