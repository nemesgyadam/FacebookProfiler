"""
Data handler module for Facebook profile data.
Handles data folder checking, filtering, and preparation.
"""

import csv
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class DataHandler:
    """Handles Facebook data folder checking, filtering, and preparation."""
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize the data handler.
        
        Args:
            base_dir: Base directory for the project. If None, uses the current directory.
        """
        self.base_dir = base_dir or Path.cwd()
        self.data_dir = self.base_dir / "data"
        self.filtered_data_dir = self.base_dir / "data_filtered"
        self.required_files_csv = self.base_dir / "required_files.csv"
    
    def check_data_availability(self) -> Dict[str, bool]:
        """
        Check if data folders are available.
        
        Returns:
            Dictionary with availability status of data and filtered_data folders.
        """
        return {
            "data_available": self.data_dir.exists() and self.data_dir.is_dir(),
            "filtered_data_available": self.filtered_data_dir.exists() and self.filtered_data_dir.is_dir()
        }
    
    def get_required_files(self) -> List[Tuple[str, bool]]:
        """
        Read required files from CSV.
        
        Returns:
            List of tuples with file path and classification.
        """
        required_files = []
        
        if not self.required_files_csv.exists():
            return required_files
        
        with open(self.required_files_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    file_path = row[0]
                    classification = row[1].lower() == 'true'
                    required_files.append((file_path, classification))
        
        return required_files
    
    def filter_data(self) -> Dict[str, any]:
        """
        Filter data from data folder to filtered_data folder based on required_files.csv.
        Excludes messages folder.
        
        Returns:
            Dictionary with filtering results.
        """
        if not self.data_dir.exists():
            return {"success": False, "error": "Data directory not found"}
        
        # Create filtered_data directory if it doesn't exist
        self.filtered_data_dir.mkdir(exist_ok=True)
        
        # Get required files
        required_files = self.get_required_files()
        
        # Copy files
        copied_files = 0
        errors = []
        
        for file_path, _ in required_files:
            # Skip messages folder
            if file_path.startswith("data\\messages") or file_path.startswith("data/messages"):
                continue
                
            source_path = self.base_dir / file_path
            target_path = self.filtered_data_dir / file_path.replace("data\\", "").replace("data/", "")
            
            try:
                # Create target directory if it doesn't exist
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file if it exists
                if source_path.exists():
                    shutil.copy2(source_path, target_path)
                    copied_files += 1
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")
        
        return {
            "success": True,
            "copied_files": copied_files,
            "errors": errors
        }
    
    def get_facebook_data_instructions(self) -> str:
        """
        Get instructions for downloading and copying Facebook data.
        
        Returns:
            HTML instructions for downloading Facebook data.
        """
        return """
        <div class="instructions">
            <h2>How to Download Your Facebook Data</h2>
            <ol>
                <li><strong>Log in to Facebook</strong> and go to your account settings.</li>
                <li>Click on <strong>Your Facebook Information</strong> in the left column.</li>
                <li>Click on <strong>Download Your Information</strong>.</li>
                <li>Select the following options:
                    <ul>
                        <li>Date Range: <strong>All time</strong></li>
                        <li>Format: <strong>JSON</strong></li>
                        <li>Media Quality: <strong>Low</strong> (to reduce file size)</li>
                    </ul>
                </li>
                <li>Select at least these categories:
                    <ul>
                        <li>Ads and Businesses</li>
                        <li>Apps and Websites</li>
                        <li>Posts</li>
                        <li>Comments and Reactions</li>
                        <li>Friends and Followers</li>
                        <li>Profile Information</li>
                    </ul>
                </li>
                <li>Click <strong>Request a download</strong>.</li>
                <li>Facebook will notify you when your download is ready (this can take several hours).</li>
                <li>Download the ZIP file and extract it.</li>
                <li>Copy the extracted <strong>data</strong> folder to this application's directory.</li>
                <li>Refresh this page to begin analysis.</li>
            </ol>
            
            <h3>Privacy Note</h3>
            <p>Your data remains on your computer and is not uploaded anywhere. 
            This application processes your data locally.</p>
        </div>
        """
