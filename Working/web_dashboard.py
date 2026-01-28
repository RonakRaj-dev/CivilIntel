"""
Web Dashboard for Incident Detection System
Simple Flask app for uploading and analyzing videos
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from pathlib import Path
from datetime import datetime

from Model_Code.incident_audit_main import IncidentAuditSystem

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv', 'flv'}

# Create upload folder
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

# Initialize audit system (lazy loading)
audit_system = None


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_video():
    """Handle video upload and analysis"""
    global audit_system

    try:
        # Check if video file is present
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400

        video_file = request.files['video']

        if video_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(video_file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: mp4, avi, mov, mkv, flv'}), 400

        # Save video file
        filename = secure_filename(video_file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(filepath)

        # Get form data
        user_description = request.form.get('description', '')
        user_timestamp = request.form.get('timestamp', None)

        # Parse GPS if provided
        user_location = None
        lat = request.form.get('latitude', None)
        lon = request.form.get('longitude', None)

        if lat and lon:
            try:
                user_location = (float(lat), float(lon))
            except ValueError:
                pass

        # Initialize audit system if needed
        if audit_system is None:
            audit_system = IncidentAuditSystem()

        # Run analysis
        report = audit_system.run_audit(
            video_path=filepath,
            user_description=user_description,
            user_timestamp=user_timestamp,
            user_location=user_location
        )

        # Clean up uploaded file (optional - comment out to keep files)
        # os.remove(filepath)

        return jsonify({
            'success': True,
            'report': report
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/reports')
def list_reports():
    """List all previous reports"""
    reports_dir = Path('audit_reports')

    if not reports_dir.exists():
        return jsonify({'reports': []})

    reports = []
    for file_path in sorted(reports_dir.glob('incident_audit_*.json'), reverse=True):
        with open(file_path) as f:
            report = json.load(f)
            reports.append({
                'filename': file_path.name,
                'timestamp': report['audit_metadata']['audit_time'],
                'credibility': report['credibility_assessment']['credibility_level']
            })

    return jsonify({'reports': reports[:20]})  # Last 20 reports


@app.route('/report/<filename>')
def get_report(filename):
    """Get specific report"""
    file_path = Path('audit_reports') / filename

    if not file_path.exists():
        return jsonify({'error': 'Report not found'}), 404

    with open(file_path) as f:
        report = json.load(f)

    return jsonify(report)


if __name__ == '__main__':
    print("=" * 70)
    print("INCIDENT DETECTION SYSTEM - WEB DASHBOARD")
    print("=" * 70)
    print("Starting server...")
    print("Open your browser to: http://localhost:5000")
    print("=" * 70)

    app.run(debug=True, host='0.0.0.0', port=5000)
