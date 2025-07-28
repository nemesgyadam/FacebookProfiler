"""
Core JSON parser for Facebook data export files
Handles encoding issues and provides safe parsing utilities
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


class FacebookDataParser:
    """Base parser for Facebook JSON data files"""
    
    def __init__(self, data_root: Union[str, Path]):
        self.data_root = Path(data_root)
        self.logger = logging.getLogger(__name__)
        
    def safe_load_json(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Safely load JSON file with encoding fallback
        Facebook exports can have encoding issues
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.logger.warning(f"File not found: {file_path}")
            return None
            
        # Try different encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    data = json.load(f)
                    self.logger.debug(f"Successfully loaded {file_path} with {encoding}")
                    return data
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                self.logger.debug(f"Failed to load {file_path} with {encoding}: {e}")
                continue
                
        self.logger.error(f"Could not load {file_path} with any encoding")
        return None
        
    def parse_facebook_timestamp(self, timestamp: Union[str, int]) -> Optional[datetime]:
        """
        Parse Facebook timestamp formats
        Facebook uses Unix timestamps and ISO strings
        """
        if not timestamp:
            return None
            
        try:
            # Try Unix timestamp first
            if isinstance(timestamp, (int, float)):
                return datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str) and timestamp.isdigit():
                return datetime.fromtimestamp(int(timestamp))
            else:
                # Try ISO format
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except (ValueError, OSError) as e:
            self.logger.warning(f"Could not parse timestamp {timestamp}: {e}")
            return None
            
    def extract_text_content(self, data: Dict[str, Any], 
                           text_fields: List[str] = None) -> List[str]:
        """
        Extract text content from nested JSON structure
        Common text fields in Facebook data
        """
        if text_fields is None:
            text_fields = ['data', 'text', 'content', 'message', 'title', 'name']
            
        texts = []
        
        def extract_recursive(obj, depth=0):
            if depth > 10:  # Prevent infinite recursion
                return
                
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in text_fields and isinstance(value, str):
                        texts.append(value.strip())
                    elif isinstance(value, (dict, list)):
                        extract_recursive(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item, depth + 1)
                    
        extract_recursive(data)
        return [t for t in texts if t]  # Remove empty strings
        
    def get_file_paths(self, pattern: str = "*.json") -> List[Path]:
        """Get all matching files in data directory"""
        return list(self.data_root.rglob(pattern))
        
    def validate_facebook_data_structure(self) -> Dict[str, bool]:
        """
        Validate that Facebook data export has expected structure
        Returns status of each major category
        """
        expected_dirs = [
            'ads_information',
            'apps_and_websites_off_of_facebook', 
            'connections',
            'logged_information',
            'personal_information',
            'preferences',
            'security_and_login_information',
            'your_facebook_activity'
        ]
        
        status = {}
        for dir_name in expected_dirs:
            dir_path = self.data_root / dir_name
            status[dir_name] = dir_path.exists() and dir_path.is_dir()
            
        return status
