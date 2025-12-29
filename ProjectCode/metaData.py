"""
Media & Metadata Validation System
Validates images and videos by checking EXIF metadata, timestamps, GPS, and authenticity markers
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
import exifread
import imghdr
import cv2
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')


class MediaValidator:
    """Comprehensive media validation system"""
    
    def __init__(self):
        self.results = {}
        
    def validate_media(
        self, 
        file_path: str,
        user_timestamp: Optional[str] = None,
        user_location: Optional[Tuple[float, float]] = None,
        timestamp_tolerance_minutes: int = 5
    ) -> Dict[str, Any]:
        """
        Main validation method
        
        Args:
            file_path: Path to media file
            user_timestamp: User-provided timestamp (ISO format or datetime string)
            user_location: User-provided GPS (latitude, longitude)
            timestamp_tolerance_minutes: Acceptable time difference
            
        Returns:
            Dictionary with validation results and scores
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": "File not found", "metadata_score": 0.0}
        
        # Detect file type
        file_type = self._detect_file_type(file_path)
        
        # Extract metadata
        metadata = self._extract_metadata(file_path, file_type)
        
        # Validate timestamp
        timestamp_score = self._validate_timestamp(
            metadata.get('timestamp'),
            user_timestamp,
            timestamp_tolerance_minutes
        )
        
        # Validate GPS
        gps_score = self._validate_gps(
            metadata.get('gps'),
            user_location
        )
        
        # Check image authenticity (if image)
        authenticity_score = 0.0
        authenticity_details = {}
        
        if file_type == 'image':
            authenticity_score, authenticity_details = self._check_image_authenticity(file_path)
        
        # Calculate overall metadata score
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
                "exif_timestamp": metadata.get('timestamp'),
                "user_timestamp": user_timestamp
            },
            "gps_validation": {
                "score": gps_score,
                "exif_gps": metadata.get('gps'),
                "user_gps": user_location
            },
            "authenticity": {
                "score": authenticity_score,
                "details": authenticity_details
            },
            "metadata_score": metadata_score,
            "warnings": self._generate_warnings(metadata, authenticity_details)
        }
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Detect if file is image or video"""
        img_type = imghdr.what(file_path)
        
        if img_type:
            return 'image'
        
        # Check video extensions
        video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v'}
        if file_path.suffix.lower() in video_exts:
            return 'video'
        
        return 'unknown'
    
    def _extract_metadata(self, file_path: Path, file_type: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from media file"""
        metadata = {
            'timestamp': None,
            'gps': None,
            'camera_model': None,
            'camera_make': None,
            'orientation': None,
            'software': None,
            'has_metadata': False,
            'metadata_count': 0
        }
        
        if file_type == 'image':
            metadata.update(self._extract_image_metadata(file_path))
        elif file_type == 'video':
            metadata.update(self._extract_video_metadata(file_path))
        
        return metadata
    
    def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract EXIF metadata from image"""
        metadata = {}
        
        try:
            # Use Pillow for basic EXIF
            with Image.open(file_path) as img:
                exif_data = img._getexif()
                
                if exif_data:
                    metadata['has_metadata'] = True
                    metadata['metadata_count'] = len(exif_data)
                    
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        
                        if tag == 'DateTime' or tag == 'DateTimeOriginal':
                            metadata['timestamp'] = self._parse_exif_datetime(value)
                        elif tag == 'Make':
                            metadata['camera_make'] = value
                        elif tag == 'Model':
                            metadata['camera_model'] = value
                        elif tag == 'Orientation':
                            metadata['orientation'] = value
                        elif tag == 'Software':
                            metadata['software'] = value
                        elif tag == 'GPSInfo':
                            metadata['gps'] = self._parse_gps(value)
            
            # Use exifread for more robust extraction
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f)
                
                # Try to get GPS if not found
                if not metadata.get('gps'):
                    gps_lat = tags.get('GPS GPSLatitude')
                    gps_lon = tags.get('GPS GPSLongitude')
                    
                    if gps_lat and gps_lon:
                        metadata['gps'] = self._convert_gps_exifread(tags)
                
                # Get additional timestamp formats
                if not metadata.get('timestamp'):
                    for tag_name in ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime']:
                        if tag_name in tags:
                            metadata['timestamp'] = self._parse_exif_datetime(str(tags[tag_name]))
                            break
        
        except Exception as e:
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from video file"""
        metadata = {}
        
        try:
            # Use OpenCV to read video
            cap = cv2.VideoCapture(str(file_path))
            
            if cap.isOpened():
                metadata['has_metadata'] = True
                metadata['fps'] = cap.get(cv2.CAP_PROP_FPS)
                metadata['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                metadata['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                metadata['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # Try to get creation time from file system
                creation_time = file_path.stat().st_ctime
                metadata['timestamp'] = datetime.fromtimestamp(creation_time)
            
            cap.release()
            
        except Exception as e:
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    def _parse_exif_datetime(self, dt_str: str) -> Optional[datetime]:
        """Parse EXIF datetime string"""
        try:
            # EXIF format: "YYYY:MM:DD HH:MM:SS"
            return datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
        except:
            try:
                # Alternative format
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except:
                return None
    
    def _parse_gps(self, gps_info: Dict) -> Optional[Tuple[float, float]]:
        """Parse GPS coordinates from EXIF GPSInfo"""
        try:
            gps_data = {}
            for tag_id, value in gps_info.items():
                tag = GPSTAGS.get(tag_id, tag_id)
                gps_data[tag] = value
            
            lat = self._convert_to_degrees(gps_data.get('GPSLatitude'))
            lon = self._convert_to_degrees(gps_data.get('GPSLongitude'))
            
            if lat and lon:
                # Handle N/S and E/W
                if gps_data.get('GPSLatitudeRef') == 'S':
                    lat = -lat
                if gps_data.get('GPSLongitudeRef') == 'W':
                    lon = -lon
                
                return (lat, lon)
        except:
            pass
        
        return None
    
    def _convert_to_degrees(self, value) -> Optional[float]:
        """Convert GPS coordinates to degrees"""
        try:
            d, m, s = value
            return float(d) + float(m) / 60.0 + float(s) / 3600.0
        except:
            return None
    
    def _convert_gps_exifread(self, tags: Dict) -> Optional[Tuple[float, float]]:
        """Convert GPS from exifread format"""
        try:
            lat = tags.get('GPS GPSLatitude')
            lon = tags.get('GPS GPSLongitude')
            lat_ref = tags.get('GPS GPSLatitudeRef')
            lon_ref = tags.get('GPS GPSLongitudeRef')
            
            if lat and lon:
                lat_val = self._dms_to_decimal(lat.values)
                lon_val = self._dms_to_decimal(lon.values)
                
                if str(lat_ref) == 'S':
                    lat_val = -lat_val
                if str(lon_ref) == 'W':
                    lon_val = -lon_val
                
                return (lat_val, lon_val)
        except:
            pass
        
        return None
    
    def _dms_to_decimal(self, dms) -> float:
        """Convert degrees, minutes, seconds to decimal"""
        d = float(dms[0].num) / float(dms[0].den)
        m = float(dms[1].num) / float(dms[1].den)
        s = float(dms[2].num) / float(dms[2].den)
        return d + m / 60.0 + s / 3600.0
    
    def _validate_timestamp(
        self, 
        exif_timestamp: Optional[datetime],
        user_timestamp: Optional[str],
        tolerance_minutes: int
    ) -> float:
        """Validate timestamp against user input"""
        if not exif_timestamp or not user_timestamp:
            return 0.5 if not exif_timestamp else 0.7
        
        try:
            # Parse user timestamp
            user_dt = None
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"]:
                try:
                    user_dt = datetime.strptime(user_timestamp, fmt)
                    break
                except:
                    continue
            
            if not user_dt:
                user_dt = datetime.fromisoformat(user_timestamp.replace('Z', '+00:00'))
            
            # Compare timestamps
            time_diff = abs((exif_timestamp - user_dt).total_seconds() / 60)
            
            if time_diff < tolerance_minutes:
                return 1.0
            elif time_diff < tolerance_minutes * 2:
                return 0.8
            elif time_diff < tolerance_minutes * 5:
                return 0.5
            else:
                return 0.2
        
        except Exception as e:
            return 0.3
    
    def _validate_gps(
        self,
        exif_gps: Optional[Tuple[float, float]],
        user_gps: Optional[Tuple[float, float]]
    ) -> float:
        """Validate GPS coordinates"""
        if not exif_gps or not user_gps:
            return 0.5 if not exif_gps else 0.7
        
        try:
            # Calculate distance using Haversine formula
            lat1, lon1 = exif_gps
            lat2, lon2 = user_gps
            
            R = 6371  # Earth radius in km
            
            dlat = np.radians(lat2 - lat1)
            dlon = np.radians(lon2 - lon1)
            
            a = (np.sin(dlat / 2) ** 2 + 
                 np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * 
                 np.sin(dlon / 2) ** 2)
            
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
            distance = R * c * 1000  # in meters
            
            if distance < 100:
                return 1.0
            elif distance < 500:
                return 0.8
            elif distance < 1000:
                return 0.6
            elif distance < 5000:
                return 0.4
            else:
                return 0.2
        
        except:
            return 0.3
    
    def _check_image_authenticity(self, file_path: Path) -> Tuple[float, Dict]:
        """Check image for signs of tampering"""
        details = {}
        scores = []
        
        try:
            img = cv2.imread(str(file_path))
            
            if img is None:
                return 0.0, {"error": "Cannot load image"}
            
            # 1. Noise Level Analysis
            noise_score = self._check_noise_level(img)
            scores.append(noise_score)
            details['noise_analysis'] = {
                'score': noise_score,
                'status': 'normal' if noise_score > 0.6 else 'suspicious'
            }
            
            # 2. JPEG Compression Analysis
            jpeg_score = self._check_jpeg_artifacts(file_path)
            scores.append(jpeg_score)
            details['jpeg_analysis'] = {
                'score': jpeg_score,
                'status': 'consistent' if jpeg_score > 0.6 else 'inconsistent'
            }
            
            # 3. ELA (Error Level Analysis)
            ela_score = self._error_level_analysis(file_path)
            scores.append(ela_score)
            details['ela_analysis'] = {
                'score': ela_score,
                'status': 'authentic' if ela_score > 0.6 else 'possibly_edited'
            }
            
            # 4. Metadata Presence Check
            metadata_score = self._check_metadata_presence(file_path)
            scores.append(metadata_score)
            details['metadata_presence'] = {
                'score': metadata_score,
                'status': 'present' if metadata_score > 0.5 else 'missing_or_stripped'
            }
            
            overall_score = np.mean(scores)
            return overall_score, details
        
        except Exception as e:
            return 0.0, {"error": str(e)}
    
    def _check_noise_level(self, img: np.ndarray) -> float:
        """Check for irregular noise patterns"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calculate noise using Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            # Split into blocks and check consistency
            h, w = gray.shape
            block_size = 64
            variances = []
            
            for i in range(0, h - block_size, block_size):
                for j in range(0, w - block_size, block_size):
                    block = gray[i:i+block_size, j:j+block_size]
                    lap = cv2.Laplacian(block, cv2.CV_64F)
                    variances.append(lap.var())
            
            if len(variances) > 0:
                # Check coefficient of variation
                cv_value = np.std(variances) / (np.mean(variances) + 1e-10)
                
                # Lower CV = more consistent noise = more authentic
                if cv_value < 0.5:
                    return 0.9
                elif cv_value < 1.0:
                    return 0.7
                else:
                    return 0.4
            
            return 0.5
        
        except:
            return 0.5
    
    def _check_jpeg_artifacts(self, file_path: Path) -> float:
        """Check for JPEG compression artifacts"""
        try:
            # Check if file is JPEG
            if file_path.suffix.lower() not in ['.jpg', '.jpeg']:
                return 0.7
            
            img = cv2.imread(str(file_path), cv2.IMREAD_GRAYSCALE)
            
            # Check for blocking artifacts (8x8 DCT blocks)
            h, w = img.shape
            diffs = []
            
            # Check horizontal edges of 8x8 blocks
            for i in range(8, h, 8):
                for j in range(0, w - 1):
                    diff = abs(int(img[i, j]) - int(img[i-1, j]))
                    diffs.append(diff)
            
            avg_diff = np.mean(diffs) if diffs else 0
            
            # Consistent blocking = authentic JPEG
            if 2 < avg_diff < 10:
                return 0.9
            elif avg_diff < 15:
                return 0.7
            else:
                return 0.5
        
        except:
            return 0.5
    
    def _error_level_analysis(self, file_path: Path) -> float:
        """Perform Error Level Analysis (ELA)"""
        try:
            if file_path.suffix.lower() not in ['.jpg', '.jpeg']:
                return 0.7
            
            # Open and resave at known quality
            img = Image.open(file_path)
            
            # Save at quality 90
            temp_path = file_path.parent / f"temp_ela_{file_path.name}"
            img.save(temp_path, 'JPEG', quality=90)
            
            # Load both images
            original = cv2.imread(str(file_path))
            resaved = cv2.imread(str(temp_path))
            
            # Calculate difference
            diff = cv2.absdiff(original, resaved)
            
            # Analyze difference
            ela_value = np.mean(diff)
            
            # Clean up
            temp_path.unlink()
            
            # Lower ELA = less editing
            if ela_value < 10:
                return 0.9
            elif ela_value < 20:
                return 0.7
            elif ela_value < 40:
                return 0.5
            else:
                return 0.3
        
        except:
            return 0.5
    
    def _check_metadata_presence(self, file_path: Path) -> float:
        """Check if metadata is present and complete"""
        try:
            with Image.open(file_path) as img:
                exif_data = img._getexif()
                
                if not exif_data:
                    return 0.2  # No metadata - suspicious
                
                # Check for important tags
                important_tags = ['DateTime', 'Make', 'Model']
                present = sum(1 for tag_id in exif_data.keys() 
                            if TAGS.get(tag_id) in important_tags)
                
                if len(exif_data) > 20 and present >= 2:
                    return 1.0
                elif len(exif_data) > 10:
                    return 0.7
                else:
                    return 0.4
        
        except:
            return 0.3
    
    def _calculate_metadata_score(
        self,
        timestamp_score: float,
        gps_score: float,
        authenticity_score: float,
        metadata: Dict
    ) -> float:
        """Calculate overall metadata score"""
        weights = {
            'timestamp': 0.25,
            'gps': 0.25,
            'authenticity': 0.35,
            'metadata_presence': 0.15
        }
        
        metadata_presence_score = 1.0 if metadata.get('has_metadata') else 0.2
        
        score = (
            timestamp_score * weights['timestamp'] +
            gps_score * weights['gps'] +
            authenticity_score * weights['authenticity'] +
            metadata_presence_score * weights['metadata_presence']
        )
        
        return round(score, 3)
    
    def _generate_warnings(self, metadata: Dict, authenticity: Dict) -> list:
        """Generate warnings based on validation results"""
        warnings = []
        
        if not metadata.get('has_metadata'):
            warnings.append("⚠️ No EXIF metadata found - file may have been edited or metadata stripped")
        
        if metadata.get('software'):
            software = metadata['software'].lower()
            if any(editor in software for editor in ['photoshop', 'gimp', 'lightroom']):
                warnings.append(f"⚠️ Image edited with {metadata['software']}")
        
        if authenticity.get('ela_analysis', {}).get('status') == 'possibly_edited':
            warnings.append("⚠️ Error Level Analysis suggests possible editing")
        
        if authenticity.get('noise_analysis', {}).get('status') == 'suspicious':
            warnings.append("⚠️ Irregular noise patterns detected")
        
        if not metadata.get('timestamp'):
            warnings.append("⚠️ No timestamp found in metadata")
        
        if not metadata.get('gps'):
            warnings.append("⚠️ No GPS coordinates found in metadata")
        
        return warnings


# Example usage
if __name__ == "__main__":
    validator = MediaValidator()
    
    # Example validation
    results = validator.validate_media(
        file_path="path/to/image.jpg",
        user_timestamp="2024-01-15 14:30:00",
        user_location=(37.7749, -122.4194),  # San Francisco coordinates
        timestamp_tolerance_minutes=5
    )
    
    # Print results
    print(json.dumps(results, indent=2, default=str))
    print(f"\n📊 Overall Metadata Score: {results['metadata_score']:.3f}")
    
    if results['warnings']:
        print("\n⚠️ Warnings:")
        for warning in results['warnings']:
            print(f"  {warning}")