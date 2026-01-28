"""
Incident Audit System - Main Entry Point
Combines threat detection and metadata validation for comprehensive incident analysis
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from media_validator import MediaValidator
from video_safety_engine import VideoSafetyEngine


class IncidentAuditSystem:
    """
    Complete incident audit system that:
    1. Validates video metadata for authenticity
    2. Detects safety threats in video content
    3. Generates comprehensive audit reports
    """

    def __init__(self):
        """Initialize the audit system"""
        self.safety_engine = None
        self.metadata_validator = MediaValidator()

    def run_audit(
            self,
            video_path: str,
            user_description: str,
            user_timestamp: Optional[str] = None,
            user_location: Optional[Tuple[float, float]] = None,
            output_dir: str = "audit_reports"
    ) -> dict:
        """
        Run complete incident audit

        Args:
            video_path: Path to video file
            user_description: User's description of the incident
            user_timestamp: When the incident occurred (ISO format)
            user_location: GPS coordinates (latitude, longitude)
            output_dir: Directory to save reports

        Returns:
            Complete audit report
        """
        print("=" * 70)
        print("INCIDENT AUDIT SYSTEM")
        print("=" * 70)
        print(f"📅 Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 User Description: {user_description}")
        print(f"📍 Video Source: {video_path}")
        print("=" * 70)

        # Validate video file
        video_path = Path(video_path)
        if not video_path.exists():
            error_msg = f"❌ Error: Video file not found: {video_path}"
            print(error_msg)
            return {"error": error_msg, "success": False}

        # Step 1: Metadata Validation
        print("\n🔍 STEP 1: METADATA VALIDATION")
        print("-" * 70)

        metadata_results = self.metadata_validator.validate_media(
            file_path=str(video_path),
            user_timestamp=user_timestamp,
            user_location=user_location
        )

        print(f"✅ Metadata Score: {metadata_results.get('metadata_score', 0):.3f}")
        print(f"   - Timestamp Match: {metadata_results.get('timestamp_validation', {}).get('score', 0):.2f}")
        print(f"   - GPS Match: {metadata_results.get('gps_validation', {}).get('score', 0):.2f}")
        print(f"   - Authenticity: {metadata_results.get('authenticity', {}).get('score', 0):.2f}")

        if metadata_results.get('warnings'):
            print("\n⚠️  Warnings:")
            for warning in metadata_results['warnings']:
                print(f"   {warning}")

        # Step 2: Threat Detection
        print("\n🔍 STEP 2: THREAT DETECTION")
        print("-" * 70)

        # Initialize safety engine (lazy loading)
        if self.safety_engine is None:
            try:
                self.safety_engine = VideoSafetyEngine(frame_interval=60)
            except Exception as e:
                print(f"⚠️  Warning: Could not load threat detection model: {e}")
                print("   Continuing with metadata validation only...")
                threat_results = {
                    "error": str(e),
                    "summary": {
                        "threat_detected": False,
                        "threat_level": "unknown"
                    }
                }

        if self.safety_engine:
            threat_results = self.safety_engine.analyze_video(str(video_path))

            summary = threat_results.get("summary", {})
            print(f"✅ Threat Analysis Complete")
            print(f"   - Threat Detected: {summary.get('threat_detected', False)}")
            print(f"   - Threat Level: {summary.get('threat_level', 'unknown').upper()}")
            print(f"   - Dominant Category: {summary.get('dominant_category', 'N/A')}")
            print(f"   - Confidence: {summary.get('max_confidence', 0):.3f}")

            if summary.get('key_threat_moments'):
                print("\n   Key Threat Moments:")
                for i, moment in enumerate(summary['key_threat_moments'][:3], 1):
                    print(f"   {i}. {moment['timestamp']} - {moment['category']} "
                          f"({moment['confidence']:.2f})")

        # Step 3: Combined Assessment
        print("\n🔍 STEP 3: CREDIBILITY ASSESSMENT")
        print("-" * 70)

        combined_assessment = self._assess_credibility(
            threat_results if self.safety_engine else {},
            metadata_results,
            user_description
        )

        print(f"✅ Overall Credibility: {combined_assessment['credibility_level'].upper()}")
        print(f"   - Credibility Score: {combined_assessment['credibility_score']:.3f}")
        print(f"   - Recommendation: {combined_assessment['recommendation']}")

        if combined_assessment.get('red_flags'):
            print("\n🚩 Red Flags:")
            for flag in combined_assessment['red_flags']:
                print(f"   {flag}")

        # Create comprehensive report
        report = {
            "audit_metadata": {
                "audit_time": datetime.now().isoformat(),
                "video_file": str(video_path),
                "video_exists": video_path.exists(),
                "file_size_mb": round(video_path.stat().st_size / (1024 * 1024), 2) if video_path.exists() else 0
            },
            "user_input": {
                "description": user_description,
                "timestamp": user_timestamp,
                "location": user_location
            },
            "metadata_validation": metadata_results,
            "threat_detection": threat_results if self.safety_engine else {"error": "Model not loaded"},
            "credibility_assessment": combined_assessment
        }

        # Save report
        output_path = self._save_report(report, output_dir)

        print("\n" + "=" * 70)
        print(f"📊 AUDIT COMPLETE")
        print(f"📁 Report saved: {output_path}")
        print("=" * 70)

        return report

    def _assess_credibility(
            self,
            threat_results: dict,
            metadata_results: dict,
            user_description: str
    ) -> dict:
        """Assess overall credibility of the incident report"""

        # Get scores
        threat_score = 0.5  # Default if no threat detection
        if "summary" in threat_results and "max_confidence" in threat_results["summary"]:
            threat_score = threat_results["summary"]["max_confidence"]

        metadata_score = metadata_results.get("metadata_score", 0.5)

        # Description quality score (simple heuristic)
        description_score = self._assess_description_quality(user_description)

        # Weighted credibility score
        credibility_score = (
                threat_score * 0.50 +  # 50% weight on threat detection
                metadata_score * 0.35 +  # 35% weight on metadata
                description_score * 0.15  # 15% weight on description
        )

        # Determine credibility level
        if credibility_score >= 0.75:
            credibility = "high"
            recommendation = "✅ Report verified - High confidence in authenticity and threat"
        elif credibility_score >= 0.55:
            credibility = "medium"
            recommendation = "⚠️  Report likely authentic - Moderate confidence, proceed with caution"
        elif credibility_score >= 0.35:
            credibility = "low"
            recommendation = "❌ Report questionable - Low confidence, requires manual review"
        else:
            credibility = "very_low"
            recommendation = "🚨 Report unreliable - Possible fabrication or heavily manipulated"

        # Identify red flags
        red_flags = []

        # Metadata red flags
        if metadata_score < 0.3:
            red_flags.append("🚨 Critical: Very low metadata score")

        if metadata_results.get("warnings"):
            red_flags.extend(metadata_results["warnings"])

        # Threat detection red flags
        if "summary" in threat_results:
            summary = threat_results["summary"]
            if summary.get("threat_detected") and summary.get("threat_percentage", 0) < 15:
                red_flags.append("⚠️  Threat detected in very few frames - possible false positive")

        # Description red flags
        if len(user_description.split()) < 5:
            red_flags.append("⚠️  Very brief description - lacks detail")

        return {
            "credibility_score": round(credibility_score, 3),
            "credibility_level": credibility,
            "recommendation": recommendation,
            "component_scores": {
                "threat_detection": round(threat_score, 3),
                "metadata_validation": round(metadata_score, 3),
                "description_quality": round(description_score, 3)
            },
            "red_flags": red_flags
        }

    def _assess_description_quality(self, description: str) -> float:
        """Assess quality of user description"""
        if not description:
            return 0.0

        # Simple heuristics
        word_count = len(description.split())

        # Quality indicators
        has_action_words = any(word in description.lower()
                               for word in ['grabbed', 'hit', 'attacked', 'approached',
                                            'threatened', 'weapon', 'violence'])

        has_context = any(word in description.lower()
                          for word in ['behind', 'front', 'near', 'inside', 'outside',
                                       'person', 'people', 'individual'])

        # Calculate score
        score = 0.3  # Base score

        if word_count >= 10:
            score += 0.3
        elif word_count >= 5:
            score += 0.15

        if has_action_words:
            score += 0.25

        if has_context:
            score += 0.15

        return min(1.0, score)

    def _save_report(self, report: dict, output_dir: str) -> Path:
        """Save audit report to file"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"incident_audit_{timestamp}.json"
        output_path = output_dir / filename

        # Save with pretty formatting
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Also save as "latest" for easy access
        latest_path = output_dir / "latest_incident_report.json"
        with open(latest_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return output_path


def main():
    """
    Main function - Example usage
    """
    # Example configuration
    VIDEO_PATH = r"C:\Users\gamer\OneDrive\Desktop\PushpamProject\assets\harr_3.mp4"  # Replace with actual path
    USER_DESCRIPTION = ("A person walking alone is suddenly approached from behind "
                        "by another individual in what appears to be an assault attempt")
    USER_TIMESTAMP = "2024-01-27 14:30:00"
    USER_LOCATION = (37.7749, -122.4194)  # San Francisco coordinates (example)

    # Create audit system
    audit_system = IncidentAuditSystem()

    # Run audit
    report = audit_system.run_audit(
        video_path=VIDEO_PATH,
        user_description=USER_DESCRIPTION,
        user_timestamp=USER_TIMESTAMP,
        user_location=USER_LOCATION
    )

    # Display summary
    if report.get("success", True):
        print("\n" + "=" * 70)
        print("QUICK SUMMARY")
        print("=" * 70)
        assessment = report.get("credibility_assessment", {})
        print(f"Credibility: {assessment.get('credibility_level', 'unknown').upper()}")
        print(f"Score: {assessment.get('credibility_score', 0):.3f}/1.000")
        print(f"\n{assessment.get('recommendation', 'No recommendation')}")


if __name__ == "__main__":
    main()
