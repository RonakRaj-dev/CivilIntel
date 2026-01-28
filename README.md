# CivilIntel  
### Incident Detection & Verification System

## 🎯 Project Overview

CivilIntel is an AI-powered incident detection and verification system that analyzes video evidence and metadata to assess the credibility of reported public safety incidents.

The system can:

1. Detect safety threats in videos (violence, weapons, accidents, etc.)
2. Validate video authenticity using EXIF metadata
3. Generate credibility scores for incident reports
4. Identify tampering using image forensics

---

## 📋 Prerequisites

- Python 3.8 or higher
- At least 4GB RAM (8GB+ recommended)
- GPU with CUDA support (optional)
- Hugging Face account with access to the PaliGemma model

---

## 🚀 Installation Steps

### Step 1: Project Structure

incident_detection_system/
├── incident_audit_main.py
├── video_safety_engine.py
├── vision_threat_detector.py
├── media_validator.py
├── hf_auth.py
├── requirements.txt
├── .env
└── README.md

### Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

### Step 3: Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt

### Optional (GPU support):

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

### Create a .env file:

HF_TOKEN=your_huggingface_token
MODEL_NAME=google/paligemma-3b-mix-224
FRAME_INTERVAL=30
CONFIDENCE_THRESHOLD=0.6