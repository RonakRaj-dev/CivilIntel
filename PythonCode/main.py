from Paligemma_code import VideoSafetyEngine
import os
import json
from datetime import datetime

def run_incident_audit(video_file, user_note):
    if not os.path.exists(video_file):
        print(f"Error: Video File '{video_file}' not found")

    print(f"Incident report received: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"User Description: {user_note}")
    print("-"*50)

    engine = VideoSafetyEngine()

    start_time = datetime.now()
    results = engine.analyze_video(video_file)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    report = {
        "metadata": {
            "incident_time": datetime.now().isoformat(),
            "processing_time_sec": round(duration, 2),
            "video_source": video_file
        },
        "user_input": user_note,
        "ai_findings": results
    }

    print("-"*50)
    print("ANALYSIS COMPLETE")
    print(json.dumps(report, indent=4))

    with open("latest_incident_report.json", "w") as f:
        json.dump(report, f, indent=4)
        print(f"\n Full report saved to 'lastest_incident_report.json'")

if __name__ == "__main__":
    VIDEO_PATH = r"C:\Users\gamer\OneDrive\Desktop\PushpamProject\Real Life Violence Dataset\Violence\V_1.mp4"
    USER_DESCRIPTION = "A man using his phone is suddenly approached from behind by another individual who grabs him, indicating a possible assault or theft attempt indoors"

    run_incident_audit(VIDEO_PATH, USER_DESCRIPTION)
