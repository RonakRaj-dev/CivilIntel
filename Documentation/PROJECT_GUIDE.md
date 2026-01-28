# 🚀 Complete Project Execution Guide

## Project: AI-Powered Incident Detection & Video Verification System

---

## 📁 Project Structure

```
incident_detection_system/
│
├── Core Analysis Modules
│   ├── incident_audit_main.py          # Main orchestrator
│   ├── video_safety_engine.py          # Video processing & threat detection
│   ├── vision_threat_detector.py       # AI threat classification
│   └── media_validator.py              # Metadata & authenticity validation
│
├── Authentication & Configuration
│   ├── hf_auth.py                      # Hugging Face authentication
│   ├── .env                            # Environment variables (create this)
│   └── requirements.txt                # Python dependencies
│
├── Web Interface (Optional)
│   ├── web_dashboard.py                # Flask web server
│   └── templates/
│       └── index.html                  # Web UI
│
├── Data Directories (Auto-created)
│   ├── uploads/                        # Uploaded videos
│   ├── audit_reports/                  # Generated reports
│   └── temp/                           # Temporary processing files
│
└── Documentation
    ├── README.md                        # Setup & usage guide
    └── PROJECT_GUIDE.md                 # This file
```

---

## 🎯 Step-by-Step Execution

### STEP 1: Environment Setup

#### 1.1 Install Python (if needed)
- Download Python 3.8+ from python.org
- Ensure pip is installed: `python --version` and `pip --version`

#### 1.2 Create Project Directory
```bash
mkdir incident_detection_system
cd incident_detection_system
```

#### 1.3 Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 1.4 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**For GPU Support (Optional but Recommended):**
```bash
# Check if you have NVIDIA GPU
nvidia-smi

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

### STEP 2: Hugging Face Setup

#### 2.1 Create Account
1. Go to https://huggingface.co/join
2. Create free account
3. Verify email

#### 2.2 Get Access Token
1. Visit https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it "incident_detection"
4. Select "Read" permission
5. Copy the token

#### 2.3 Accept Model Terms
1. Visit https://huggingface.co/google/paligemma-3b-mix-224
2. Click "Agree and access repository"
3. Fill out the form if required

#### 2.4 Configure Token
Create `.env` file in project root:
```env
HF_TOKEN=hf_your_token_here
```

Or use the authentication helper:
```bash
python hf_auth.py
# Enter token when prompted
```

---

### STEP 3: Test Installation

#### 3.1 Quick System Test
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}')"
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "from transformers import AutoProcessor; print('Transformers: OK')"
```

#### 3.2 Test Vision Model (Optional)
```python
from vision_threat_detector import VisionThreatDetector
from PIL import Image

# Create test image
img = Image.new('RGB', (224, 224), color='white')

# Load detector (this will download the model ~3GB first time)
detector = VisionThreatDetector()

# Test analysis
result = detector.analyze(img)
print(result)
```

---

### STEP 4: Prepare Test Data

#### 4.1 Get Sample Videos
Options:
- Use your own video files
- Download from: https://www.pexels.com/videos/ (free stock videos)
- Create test videos with your phone camera

#### 4.2 Place Videos
```
incident_detection_system/
└── test_videos/
    ├── sample1.mp4
    ├── sample2.mp4
    └── sample3.mp4
```

---

### STEP 5: Run Analysis (3 Methods)

#### Method 1: Python Script (Recommended for Testing)

Edit `incident_audit_main.py` at the bottom:

```python
if __name__ == "__main__":
    VIDEO_PATH = "test_videos/sample1.mp4"  # Your video
    USER_DESCRIPTION = "Person walking alone suddenly approached from behind"
    USER_TIMESTAMP = "2024-01-27 14:30:00"
    USER_LOCATION = (37.7749, -122.4194)  # Optional
    
    audit_system = IncidentAuditSystem()
    report = audit_system.run_audit(
        video_path=VIDEO_PATH,
        user_description=USER_DESCRIPTION,
        user_timestamp=USER_TIMESTAMP,
        user_location=USER_LOCATION
    )
```

Run:
```bash
python incident_audit_main.py
```

#### Method 2: Interactive Python
```python
from incident_audit_main import IncidentAuditSystem

audit = IncidentAuditSystem()

# Analyze video
report = audit.run_audit(
    video_path="test_videos/sample1.mp4",
    user_description="Describe the incident here",
    user_timestamp="2024-01-27 14:30:00",
    user_location=(37.7749, -122.4194)
)

# Print credibility
print(f"Credibility: {report['credibility_assessment']['credibility_level']}")
print(f"Score: {report['credibility_assessment']['credibility_score']}")
```

#### Method 3: Web Dashboard (Best for Production)
```bash
# Add Flask to requirements
pip install flask

# Start server
python web_dashboard.py
```

Then open browser to: http://localhost:5000

---

### STEP 6: Understanding Results

#### Output Structure
```json
{
  "audit_metadata": {
    "audit_time": "2024-01-27T14:30:00",
    "video_file": "sample.mp4"
  },
  "credibility_assessment": {
    "credibility_score": 0.75,
    "credibility_level": "high",
    "recommendation": "Report verified - high confidence",
    "component_scores": {
      "threat_detection": 0.85,
      "metadata_validation": 0.65,
      "description_quality": 0.70
    },
    "red_flags": []
  },
  "threat_detection": {
    "summary": {
      "threat_detected": true,
      "threat_level": "high",
      "dominant_category": "physical_violence",
      "max_confidence": 0.85
    }
  },
  "metadata_validation": {
    "metadata_score": 0.65,
    "authenticity": {
      "score": 0.70
    },
    "warnings": []
  }
}
```

#### Interpreting Scores

**Credibility Score (0-1)**
- 0.75-1.0: HIGH - Report is authentic and credible
- 0.55-0.74: MEDIUM - Likely authentic, needs review
- 0.35-0.54: LOW - Questionable, manual verification required
- 0.0-0.34: VERY LOW - Likely fake or manipulated

**Component Breakdown**
- **Threat Detection (50%)**: AI confidence in detecting threats
- **Metadata Validation (35%)**: EXIF data authenticity
- **Description Quality (15%)**: User description coherence

---

### STEP 7: Advanced Configuration

#### Tune Performance
Edit `video_safety_engine.py`:

```python
# Faster processing (fewer frames)
engine = VideoSafetyEngine(frame_interval=60)  # Default: 30

# More thorough (more frames)
engine = VideoSafetyEngine(frame_interval=15)

# Adjust confidence threshold
engine = VideoSafetyEngine(confidence_threshold=0.7)  # Default: 0.6
```

#### Customize Threat Categories
Edit `vision_threat_detector.py`:

```python
ALLOWED_CATEGORIES = [
    "physical_violence",
    "weapon_presence",
    "injured_person",
    "harassment",
    "crowd_aggression",
    "fire_or_explosion",
    "accident",
    "vandalism",          # Add custom
    "trespassing",        # Add custom
    "non_threat"
]
```

---

### STEP 8: Production Deployment

#### 8.1 Database Integration
```python
# Add to requirements.txt
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0

# Example: Save to PostgreSQL
from sqlalchemy import create_engine
import json

engine = create_engine('postgresql://user:pass@localhost/incidents')

with engine.connect() as conn:
    conn.execute("""
        INSERT INTO incident_reports (report_data, credibility_score, timestamp)
        VALUES (%s, %s, %s)
    """, (json.dumps(report), report['credibility_assessment']['credibility_score'], datetime.now()))
```

#### 8.2 API Deployment
```python
# Add to requirements.txt
fastapi>=0.104.0
uvicorn>=0.24.0

# Create api.py
from fastapi import FastAPI, UploadFile
from incident_audit_main import IncidentAuditSystem

app = FastAPI()
audit = IncidentAuditSystem()

@app.post("/analyze")
async def analyze(video: UploadFile, description: str):
    # Save video temporarily
    with open(f"temp/{video.filename}", "wb") as f:
        f.write(await video.read())
    
    # Analyze
    report = audit.run_audit(
        video_path=f"temp/{video.filename}",
        user_description=description
    )
    
    return report

# Run: uvicorn api:app --reload
```

#### 8.3 Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "web_dashboard.py"]
```

Build and run:
```bash
docker build -t incident-detection .
docker run -p 5000:5000 incident-detection
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Model not found" or "Access denied"
✅ Solution:
```bash
# Re-authenticate
huggingface-cli login

# Or update .env
HF_TOKEN=hf_your_new_token
```

#### 2. Out of Memory
✅ Solutions:
- Increase frame_interval: `VideoSafetyEngine(frame_interval=60)`
- Use CPU: Edit `vision_threat_detector.py` → `device_map="cpu"`
- Process shorter clips

#### 3. Slow Processing
✅ Solutions:
- Install CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu118`
- Reduce frame sampling
- Use smaller model (if available)

#### 4. Video Can't Open
✅ Solutions:
```bash
# Install codecs
pip install opencv-python-headless

# Convert video
ffmpeg -i input.avi -c:v libx264 output.mp4
```

#### 5. Import Errors
✅ Solution:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt --force-reinstall
```

---

## 📊 Performance Benchmarks

| Hardware | Frame Interval | Processing Time (60s video) |
|----------|---------------|----------------------------|
| CPU Only (i7) | 30 | ~8 minutes |
| CPU Only (i7) | 60 | ~4 minutes |
| GPU (RTX 3060) | 30 | ~2 minutes |
| GPU (RTX 3060) | 60 | ~1 minute |

---

## 🎓 Next Steps & Enhancements

### Phase 1: Core Improvements
- [ ] Add audio analysis (detect screams, gunshots)
- [ ] Implement object tracking across frames
- [ ] Add face detection and blurring (privacy)
- [ ] Support more video formats

### Phase 2: Advanced Features
- [ ] Real-time stream processing
- [ ] Multi-video comparison
- [ ] Automatic summary generation
- [ ] Alert notification system

### Phase 3: Production Ready
- [ ] RESTful API
- [ ] User authentication
- [ ] Report management dashboard
- [ ] Batch processing
- [ ] Cloud deployment (AWS/Azure)

### Phase 4: AI Enhancements
- [ ] Fine-tune model on custom dataset
- [ ] Add temporal analysis (action recognition)
- [ ] Implement deepfake detection
- [ ] Multi-modal analysis (audio + video + text)

---

## 📝 Code Examples

### Batch Processing
```python
from pathlib import Path
from incident_audit_main import IncidentAuditSystem

audit = IncidentAuditSystem()

videos_dir = Path("test_videos")
for video_file in videos_dir.glob("*.mp4"):
    print(f"Processing: {video_file.name}")
    
    report = audit.run_audit(
        video_path=str(video_file),
        user_description="Automated batch processing"
    )
    
    score = report['credibility_assessment']['credibility_score']
    print(f"  → Credibility: {score:.3f}\n")
```

### Custom Scoring
```python
def custom_assessment(threat_score, metadata_score, description_score):
    """Your custom credibility algorithm"""
    
    # Example: Prioritize threat detection more
    weights = {
        'threat': 0.70,      # 70%
        'metadata': 0.20,    # 20%
        'description': 0.10  # 10%
    }
    
    return (
        threat_score * weights['threat'] +
        metadata_score * weights['metadata'] +
        description_score * weights['description']
    )
```

### Notification System
```python
import smtplib
from email.mime.text import MIMEText

def send_alert(report, threshold=0.75):
    """Send email alert for high-credibility threats"""
    
    credibility = report['credibility_assessment']['credibility_score']
    
    if credibility >= threshold:
        msg = MIMEText(f"""
        HIGH CREDIBILITY INCIDENT DETECTED
        
        Score: {credibility:.3f}
        Category: {report['threat_detection']['summary']['dominant_category']}
        Time: {report['audit_metadata']['audit_time']}
        
        Review immediately.
        """)
        
        msg['Subject'] = '🚨 High-Priority Incident Alert'
        msg['From'] = 'system@example.com'
        msg['To'] = 'security@example.com'
        
        # Send email (configure SMTP)
        # smtp = smtplib.SMTP('smtp.gmail.com', 587)
        # smtp.send_message(msg)
```

---

## 🎯 Success Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list`)
- [ ] Hugging Face token configured
- [ ] Model downloaded (first run takes time)
- [ ] Test video analyzed successfully
- [ ] Results saved to `audit_reports/`
- [ ] Web dashboard accessible (optional)

---

## 📞 Support Resources

- **Hugging Face**: https://huggingface.co/docs
- **OpenCV**: https://docs.opencv.org/
- **PyTorch**: https://pytorch.org/docs/
- **Transformers**: https://huggingface.co/docs/transformers/

---

## ✅ Final Validation

Run this complete test:

```python
from incident_audit_main import IncidentAuditSystem
from pathlib import Path

# Create test system
audit = IncidentAuditSystem()

# Check if model loads
try:
    audit.safety_engine = VideoSafetyEngine()
    print("✅ Threat detection model loaded")
except Exception as e:
    print(f"❌ Model error: {e}")

# Check metadata validator
try:
    validator = MediaValidator()
    print("✅ Metadata validator initialized")
except Exception as e:
    print(f"❌ Validator error: {e}")

# Test with sample video
test_video = "test_videos/sample1.mp4"
if Path(test_video).exists():
    report = audit.run_audit(
        video_path=test_video,
        user_description="Test analysis"
    )
    print(f"✅ Analysis complete: {report['credibility_assessment']['credibility_level']}")
else:
    print("⚠️  No test video found - create test_videos/sample1.mp4")

print("\n🎉 System validation complete!")
```

---

**You're now ready to use the Incident Detection System!**
