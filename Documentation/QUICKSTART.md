# 🚀 QUICK START GUIDE - Execute in 5 Minutes

## What This System Does

This AI-powered system analyzes videos to:
1. **Detect threats** (violence, weapons, accidents) using vision AI
2. **Verify authenticity** through EXIF metadata analysis
3. **Generate credibility scores** for incident reports
4. **Identify tampering** using image forensics

---

## ⚡ Quick Setup (5 Steps)

### 1️⃣ Install Dependencies (2 min)

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install packages
pip install -r requirements.txt
```

### 2️⃣ Get Hugging Face Token (1 min)

1. Go to: https://huggingface.co/settings/tokens
2. Create token (Read permission)
3. Accept model terms: https://huggingface.co/google/paligemma-3b-mix-224

### 3️⃣ Configure Token (30 sec)

Create `.env` file:
```env
HF_TOKEN=hf_your_token_here
```

### 4️⃣ Test Installation (30 sec)

```bash
python test_system.py
```

### 5️⃣ Run Analysis (1 min)

```bash
python incident_audit_main.py
```

---

## 📊 Three Ways to Use

### Option A: Command Line (Quick Test)

Edit `incident_audit_main.py` (bottom of file):
```python
VIDEO_PATH = "your_video.mp4"
USER_DESCRIPTION = "Description of incident"
```

Run:
```bash
python incident_audit_main.py
```

### Option B: Python Script (Flexible)

```python
from incident_audit_main import IncidentAuditSystem

audit = IncidentAuditSystem()

report = audit.run_audit(
    video_path="video.mp4",
    user_description="Person attacked from behind",
    user_timestamp="2024-01-27 14:30:00",
    user_location=(37.7749, -122.4194)  # Optional
)

print(f"Credibility: {report['credibility_assessment']['credibility_level']}")
print(f"Score: {report['credibility_assessment']['credibility_score']:.3f}")
```

### Option C: Web Interface (Best UX)

```bash
pip install flask
python web_dashboard.py
```

Open browser: http://localhost:5000

---

## 🎯 Understanding Results

### Credibility Levels
- **HIGH (75-100%)**: Authentic, verified threat
- **MEDIUM (55-74%)**: Likely real, needs review  
- **LOW (35-54%)**: Questionable, manual check required
- **VERY LOW (0-34%)**: Likely fake/manipulated

### Threat Categories
- `physical_violence` - Assault, fighting
- `weapon_presence` - Visible weapons
- `injured_person` - Visible injuries
- `harassment` - Threatening behavior
- `fire_or_explosion` - Fire/explosive events
- `accident` - Traffic/other accidents
- `non_threat` - Safe/normal activity

---

## 🔧 Quick Troubleshooting

**Problem: "Model not found"**
```bash
huggingface-cli login
# Enter token, then accept model terms
```

**Problem: Out of memory**
```python
# Edit video_safety_engine.py
engine = VideoSafetyEngine(frame_interval=60)  # Analyze fewer frames
```

**Problem: Slow processing**
```bash
# Install GPU support
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

**Problem: Can't open video**
```bash
# Install codecs
pip install opencv-python-headless
```

---

## 📁 Project Files Explained

```
Your Fixed Code:
├── media_validator.py          # From your upload ✅
├── hf_auth.py                  # From your upload ✅

New Complete System:
├── incident_audit_main.py      # Main orchestrator
├── video_safety_engine.py      # Video analysis engine
├── vision_threat_detector.py   # AI threat detection
├── web_dashboard.py            # Web interface (optional)
├── test_system.py              # Validation script
└── requirements.txt            # Dependencies
```

---

## ⚙️ Configuration Options

### Adjust Processing Speed

```python
# Fast (analyze every 60th frame)
engine = VideoSafetyEngine(frame_interval=60)

# Balanced (default - every 30th frame)  
engine = VideoSafetyEngine(frame_interval=30)

# Thorough (every 15th frame)
engine = VideoSafetyEngine(frame_interval=15)
```

### Change Confidence Threshold

```python
# Stricter detection
engine = VideoSafetyEngine(confidence_threshold=0.75)

# Default
engine = VideoSafetyEngine(confidence_threshold=0.60)

# More sensitive
engine = VideoSafetyEngine(confidence_threshold=0.50)
```

---

## 📈 Performance Guide

| Setup | Processing Speed (60s video) |
|-------|----------------------------|
| CPU + frame_interval=60 | ~4 minutes |
| CPU + frame_interval=30 | ~8 minutes |
| GPU + frame_interval=60 | ~1 minute |
| GPU + frame_interval=30 | ~2 minutes |

---

## 🎓 Next Steps

### Immediate:
1. ✅ Run `python test_system.py`
2. ✅ Add test video to `test_videos/`
3. ✅ Run first analysis

### Short-term:
- Tune `frame_interval` for your needs
- Set up web dashboard for easier use
- Create database for storing reports

### Advanced:
- Add real-time stream processing
- Implement alert notifications
- Fine-tune model on custom data
- Deploy to cloud (AWS/Azure)

---

## 💡 Pro Tips

1. **First run downloads model (~3GB)** - be patient!
2. **GPU speeds up 5-10x** - install CUDA if available
3. **Shorter videos = faster** - split long videos
4. **Save reports automatically** - check `audit_reports/`
5. **Web UI is easiest** for non-technical users

---

## 🎯 Complete Example

```python
# 1. Import
from incident_audit_main import IncidentAuditSystem

# 2. Initialize
audit = IncidentAuditSystem()

# 3. Analyze
report = audit.run_audit(
    video_path="incident.mp4",
    user_description="Suspicious activity near ATM",
    user_timestamp="2024-01-27 14:30:00"
)

# 4. Check results
assessment = report['credibility_assessment']
print(f"Credibility: {assessment['credibility_level']}")
print(f"Score: {assessment['credibility_score']:.3f}")

if assessment['credibility_score'] > 0.75:
    print("✅ High confidence - Report verified")
elif assessment['credibility_score'] > 0.55:
    print("⚠️  Medium confidence - Manual review suggested")
else:
    print("❌ Low confidence - Likely false/manipulated")

# 5. View details
print("\nThreat Detection:")
threat = report['threat_detection']['summary']
print(f"  Detected: {threat['threat_detected']}")
print(f"  Category: {threat['dominant_category']}")
print(f"  Confidence: {threat['max_confidence']:.3f}")

print("\nMetadata Validation:")
metadata = report['metadata_validation']
print(f"  Authenticity: {metadata['authenticity']['score']:.3f}")
print(f"  Overall Score: {metadata['metadata_score']:.3f}")

# Report auto-saved to: audit_reports/latest_incident_report.json
```

---

## 🆘 Get Help

**Can't get it working?**
1. Run: `python test_system.py`
2. Check error messages
3. Read `PROJECT_GUIDE.md` for detailed help

**Still stuck?**
- Check Hugging Face docs: https://huggingface.co/docs
- OpenCV issues: https://docs.opencv.org/
- Model access: https://huggingface.co/google/paligemma-3b-mix-224

---

## ✅ Success Checklist

Before using the system, verify:
- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip list`)
- [ ] HF_TOKEN configured in `.env`
- [ ] Test script passes (`python test_system.py`)
- [ ] Sample video in `test_videos/` folder
- [ ] First analysis runs successfully

---

**You're ready! Start with:** `python incident_audit_main.py`

Good luck with your project! 🚀
