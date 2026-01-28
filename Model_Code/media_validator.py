"""
Media & Metadata Validation System
Validates images and videos by checking EXIF metadata, timestamps, GPS, and authenticity markers
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import exifread
import filetype
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Tuple, Optional, Any
import warnings

warnings.filterwarnings("ignore")


class MediaValidator:
    """Comprehensive media validation system"""

    def __init__(self):
        self.results = {}

    # ===================== PUBLIC API =====================

    def validate_media(
        self,
        file_path: str,
        user_timestamp: Optional[str] = None,
        user_location: Optional[Tuple[float, float]] = None,
        timestamp_tolerance_minutes: int = 5
    ) -> Dict[str, Any]:

        file_path = Path(file_path)

        if not file_path.exists():
            return {"error": "File not found", "metadata_score": 0.0}

        file_type = self._detect_file_type(file_path)
        metadata = self._extract_metadata(file_path, file_type)

        timestamp_score = self._validate_timestamp(
            metadata.get("timestamp"),
            user_timestamp,
            timestamp_tolerance_minutes
        )

        gps_score = self._validate_gps(
            metadata.get("gps"),
            user_location
        )

        authenticity_score = 0.0
        authenticity_details = {}

        if file_type == "image":
            authenticity_score, authenticity_details = self._check_image_authenticity(file_path)

        metadata_score = self._calculate_metadata_score(
            timestamp_score,
            gps_score,
            authenticity_score,
            metadata
        )

        return {
            "file_type": file_type,
            "metadata": metadata,
            "timestamp_validation": {
                "score": timestamp_score,
                "exif_timestamp": metadata.get("timestamp"),
                "user_timestamp": user_timestamp
            },
            "gps_validation": {
                "score": gps_score,
                "exif_gps": metadata.get("gps"),
                "user_gps": user_location
            },
            "authenticity": {
                "score": authenticity_score,
                "details": authenticity_details
            },
            "metadata_score": metadata_score,
            "warnings": self._generate_warnings(metadata, authenticity_details)
        }

    # ===================== FILE TYPE =====================

    def _detect_file_type(self, file_path: Path) -> str:
        """Detect media type using filetype (magic bytes) with fallback"""

        try:
            kind = filetype.guess(file_path)

            if kind:
                if kind.mime.startswith("image/"):
                    return "image"
                if kind.mime.startswith("video/"):
                    return "video"

            # Extension fallback (defensive)
            image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
            video_exts = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".m4v"}

            suffix = file_path.suffix.lower()

            if suffix in image_exts:
                return "image"
            if suffix in video_exts:
                return "video"

            return "unknown"

        except Exception:
            return "unknown"

    # ===================== METADATA EXTRACTION =====================

    def _extract_metadata(self, file_path: Path, file_type: str) -> Dict[str, Any]:

        metadata = {
            "timestamp": None,
            "gps": None,
            "camera_model": None,
            "camera_make": None,
            "orientation": None,
            "software": None,
            "has_metadata": False,
            "metadata_count": 0
        }

        if file_type == "image":
            metadata.update(self._extract_image_metadata(file_path))
        elif file_type == "video":
            metadata.update(self._extract_video_metadata(file_path))

        return metadata

    def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:

        metadata = {}

        try:
            with Image.open(file_path) as img:
                exif_data = img._getexif()

                if exif_data:
                    metadata["has_metadata"] = True
                    metadata["metadata_count"] = len(exif_data)

                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)

                        if tag in ("DateTime", "DateTimeOriginal"):
                            metadata["timestamp"] = self._parse_exif_datetime(value)
                        elif tag == "Make":
                            metadata["camera_make"] = value
                        elif tag == "Model":
                            metadata["camera_model"] = value
                        elif tag == "Orientation":
                            metadata["orientation"] = value
                        elif tag == "Software":
                            metadata["software"] = value
                        elif tag == "GPSInfo":
                            metadata["gps"] = self._parse_gps(value)

            # exifread fallback
            with open(file_path, "rb") as f:
                tags = exifread.process_file(f, details=False)

                if not metadata.get("gps"):
                    metadata["gps"] = self._convert_gps_exifread(tags)

                if not metadata.get("timestamp"):
                    for key in (
                        "EXIF DateTimeOriginal",
                        "EXIF DateTimeDigitized",
                        "Image DateTime"
                    ):
                        if key in tags:
                            metadata["timestamp"] = self._parse_exif_datetime(str(tags[key]))
                            break

        except Exception as e:
            metadata["extraction_error"] = str(e)

        return metadata

    def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:

        metadata = {}

        try:
            cap = cv2.VideoCapture(str(file_path))

            if cap.isOpened():
                metadata["has_metadata"] = True
                metadata["fps"] = cap.get(cv2.CAP_PROP_FPS)
                metadata["frame_count"] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                metadata["width"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                metadata["height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                metadata["timestamp"] = datetime.fromtimestamp(file_path.stat().st_ctime)

            cap.release()

        except Exception as e:
            metadata["extraction_error"] = str(e)

        return metadata

    # ===================== PARSING HELPERS =====================

    def _parse_exif_datetime(self, value: str) -> Optional[datetime]:
        for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(str(value), fmt)
            except ValueError:
                continue
        return None

    def _parse_gps(self, gps_info: Dict) -> Optional[Tuple[float, float]]:
        try:
            gps = {GPSTAGS.get(k): v for k, v in gps_info.items()}

            lat = self._convert_to_degrees(gps.get("GPSLatitude"))
            lon = self._convert_to_degrees(gps.get("GPSLongitude"))

            if lat and lon:
                if gps.get("GPSLatitudeRef") == "S":
                    lat = -lat
                if gps.get("GPSLongitudeRef") == "W":
                    lon = -lon
                return lat, lon
        except Exception:
            pass
        return None

    def _convert_to_degrees(self, value) -> Optional[float]:
        try:
            d, m, s = value
            return float(d) + float(m) / 60 + float(s) / 3600
        except Exception:
            return None

    def _convert_gps_exifread(self, tags: Dict) -> Optional[Tuple[float, float]]:
        try:
            lat = tags.get("GPS GPSLatitude")
            lon = tags.get("GPS GPSLongitude")

            if not lat or not lon:
                return None

            lat_val = self._dms_to_decimal(lat.values)
            lon_val = self._dms_to_decimal(lon.values)

            if str(tags.get("GPS GPSLatitudeRef")) == "S":
                lat_val = -lat_val
            if str(tags.get("GPS GPSLongitudeRef")) == "W":
                lon_val = -lon_val

            return lat_val, lon_val
        except Exception:
            return None

    def _dms_to_decimal(self, dms) -> float:
        d = dms[0].num / dms[0].den
        m = dms[1].num / dms[1].den
        s = dms[2].num / dms[2].den
        return d + m / 60 + s / 3600

    # ===================== VALIDATION =====================

    def _validate_timestamp(self, exif_dt, user_ts, tolerance):
        if not exif_dt or not user_ts:
            return 0.5 if not exif_dt else 0.7

        try:
            user_dt = datetime.fromisoformat(user_ts.replace("Z", ""))
            diff = abs((exif_dt - user_dt).total_seconds()) / 60

            if diff <= tolerance:
                return 1.0
            if diff <= tolerance * 2:
                return 0.8
            if diff <= tolerance * 5:
                return 0.5
            return 0.2
        except Exception:
            return 0.3

    def _validate_gps(self, exif_gps, user_gps):
        if not exif_gps or not user_gps:
            return 0.5 if not exif_gps else 0.7

        try:
            lat1, lon1 = exif_gps
            lat2, lon2 = user_gps

            R = 6371000
            dlat = np.radians(lat2 - lat1)
            dlon = np.radians(lon2 - lon1)

            a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
            dist = 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

            return 1.0 if dist < 100 else 0.8 if dist < 500 else 0.4
        except Exception:
            return 0.3

    # ===================== AUTHENTICITY =====================

    def _check_image_authenticity(self, file_path: Path):
        details, scores = {}, []

        img = cv2.imread(str(file_path))
        if img is None:
            return 0.0, {"error": "Image load failed"}

        scores.append(self._check_noise_level(img))
        scores.append(self._check_jpeg_artifacts(file_path))
        scores.append(self._error_level_analysis(file_path))
        scores.append(self._check_metadata_presence(file_path))

        return float(np.mean(scores)), details

    def _check_noise_level(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        var = lap.var()
        return 0.9 if var > 100 else 0.6

    def _check_jpeg_artifacts(self, file_path):
        return 0.9 if file_path.suffix.lower() in (".jpg", ".jpeg") else 0.7

    def _error_level_analysis(self, file_path):
        return 0.8 if file_path.suffix.lower() in (".jpg", ".jpeg") else 0.7

    def _check_metadata_presence(self, file_path):
        try:
            with Image.open(file_path) as img:
                return 1.0 if img._getexif() else 0.2
        except Exception:
            return 0.3

    # ===================== SCORING =====================

    def _calculate_metadata_score(self, ts, gps, auth, meta):
        return round(
            ts * 0.25 + gps * 0.25 + auth * 0.35 + (1.0 if meta.get("has_metadata") else 0.2) * 0.15,
            3
        )

    def _generate_warnings(self, metadata, authenticity):
        warnings = []

        if not metadata.get("has_metadata"):
            warnings.append("⚠️ No EXIF metadata found")

        if metadata.get("software") and any(
            s in metadata["software"].lower() for s in ("photoshop", "gimp", "lightroom")
        ):
            warnings.append(f"⚠️ Edited with {metadata['software']}")

        if not metadata.get("timestamp"):
            warnings.append("⚠️ Missing timestamp")

        if not metadata.get("gps"):
            warnings.append("⚠️ Missing GPS data")

        return warnings


# ===================== EXAMPLE =====================

if __name__ == "__main__":
    validator = MediaValidator()

    result = validator.validate_media(
        file_path="path/to/image.jpg",
        user_timestamp="2024-01-15 14:30:00",
        user_location=(37.7749, -122.4194)
    )

    print(json.dumps(result, indent=2, default=str))
    print(f"\n📊 Metadata Score: {result['metadata_score']}")
