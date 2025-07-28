#!/usr/bin/env python3
"""
Minimalistic web interface for browsing Facebook profile data.
"""

import json
import os
import csv
import sys
import subprocess
import markdown
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from .analyzers.ad_preferences import AdPreferencesAnalyzer

# Import data handler
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_handler import DataHandler


app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
FILTERED_DATA_DIR = BASE_DIR / "data_filtered"
TOKEN_COUNTS_FILE = BASE_DIR / "token_counts.csv"
PROFILE_FILE = BASE_DIR / "profile_result.md"

# Initialize data handler
data_handler = DataHandler(BASE_DIR)

# Custom filters
@app.template_filter('format_number')
def format_number(value):
    """Format number with commas as thousands separators."""
    return f"{value:,}"


class DataBrowser:
    """Simple browser for Facebook profile data."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._cache = {}
    
    def get_overview(self) -> Dict[str, Any]:
        """Get overview of all data categories."""
        overview = {}
        
        if not self.data_dir.exists():
            return {"error": "Data directory not found"}
        
        for category in self.data_dir.iterdir():
            if category.is_dir():
                category_info = self._analyze_category(category)
                overview[category.name] = category_info
        
        return overview
    
    def _analyze_category(self, category_path: Path) -> Dict[str, Any]:
        """Analyze a category directory."""
        info = {
            "name": category_path.name,
            "path": str(category_path.relative_to(self.data_dir)),
            "files": [],
            "subdirs": [],
            "total_size": 0,
            "file_count": 0
        }
        
        for item in category_path.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                info["total_size"] += size
                info["file_count"] += 1
                
                # Add file info for direct children
                if item.parent == category_path:
                    info["files"].append({
                        "name": item.name,
                        "size": size,
                        "size_human": self._format_size(size),
                        "type": item.suffix[1:] if item.suffix else "file"
                    })
            elif item.is_dir() and item.parent == category_path:
                subdir_info = self._get_dir_info(item)
                info["subdirs"].append(subdir_info)
        
        info["size_human"] = self._format_size(info["total_size"])
        return info
    
    def _get_dir_info(self, dir_path: Path) -> Dict[str, Any]:
        """Get basic info about a directory."""
        total_size = 0
        file_count = 0
        
        for item in dir_path.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
                file_count += 1
        
        return {
            "name": dir_path.name,
            "path": str(dir_path.relative_to(self.data_dir)),
            "file_count": file_count,
            "total_size": total_size,
            "size_human": self._format_size(total_size)
        }
    
    def read_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Read and return JSON file content."""
        try:
            full_path = self.data_dir / file_path
            if not full_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            if not full_path.suffix == '.json':
                return {"error": f"Not a JSON file: {file_path}"}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                return content
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {str(e)}"}
        except UnicodeDecodeError as e:
            return {"error": f"Encoding error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def search_data(self, query: str) -> List[Dict[str, Any]]:
        """Search for files and content matching query."""
        results = []
        query_lower = query.lower()
        
        for file_path in self.data_dir.rglob("*.json"):
            # Check filename
            if query_lower in file_path.name.lower():
                results.append({
                    "type": "filename",
                    "path": str(file_path.relative_to(self.data_dir)),
                    "name": file_path.name,
                    "size": self._format_size(file_path.stat().st_size),
                    "match": "filename"
                })
                continue
            
            # Check content (for smaller files)
            if file_path.stat().st_size < 100000:  # 100KB limit
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if query_lower in content.lower():
                            results.append({
                                "type": "content",
                                "path": str(file_path.relative_to(self.data_dir)),
                                "name": file_path.name,
                                "size": self._format_size(file_path.stat().st_size),
                                "match": "content"
                            })
                except:
                    pass
        
        return results[:50]  # Limit results
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f}KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f}MB"
        else:
            return f"{size_bytes/(1024**3):.1f}GB"


# Initialize data browser
browser = DataBrowser(DATA_DIR)


@app.route('/')
def index():
    """Main page showing data overview or instructions if data is missing."""
    # Check data availability
    data_status = data_handler.check_data_availability()
    
    # If filtered data is available, use it
    if data_status["filtered_data_available"]:
        browser = DataBrowser(FILTERED_DATA_DIR)
        overview = browser.get_overview()
        return render_template('index.html', 
                             overview=overview, 
                             data_status=data_status,
                             show_profile_button=PROFILE_FILE.exists())
    
    # If raw data is available, show filter option
    elif data_status["data_available"]:
        return render_template('data_filter.html', 
                             data_status=data_status,
                             instructions=data_handler.get_facebook_data_instructions())
    
    # If no data is available, show instructions
    else:
        return render_template('instructions.html', 
                             data_status=data_status,
                             instructions=data_handler.get_facebook_data_instructions())


@app.route('/category/<path:category_name>')
def category_detail(category_name: str):
    """Show detailed view of a category."""
    overview = browser.get_overview()
    category_data = overview.get(category_name)
    
    if not category_data:
        return "Category not found", 404
    
    return render_template('category.html', 
                         category=category_data, 
                         category_name=category_name)


@app.route('/file/<path:file_path>')
def view_file(file_path: str):
    """View content of a JSON file."""
    content = browser.read_json_file(file_path)
    
    if content is None:
        return "File not found", 404
    
    # Check if this is ad_preferences.json for smart analysis
    if file_path.endswith('ads_information/ad_preferences.json'):
        if not content.get('error'):
            analyzer = AdPreferencesAnalyzer(content)
            analysis = analyzer.analyze()
            return render_template('ad_preferences_analysis.html', 
                                 analysis=analysis, 
                                 file_path=file_path,
                                 raw_content=content)
    
    return render_template('file_viewer.html', 
                         content=content, 
                         file_path=file_path)


@app.route('/search')
def search_page():
    """Search results page."""
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', query='', results=[])
    
    results = browser.search_data(query)
    return render_template('search.html', query=query, results=results)


@app.route('/api/search')
def search():
    """Search API endpoint."""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = browser.search_data(query)
    return jsonify(results)


@app.route('/tokens')
def token_dashboard():
    """Token count dashboard."""
    token_data = []
    
    # Check if token counts file exists
    if not TOKEN_COUNTS_FILE.exists():
        return render_template('token_dashboard.html', 
                             token_data=[], 
                             total_tokens=0,
                             avg_tokens=0,
                             max_tokens=0,
                             top_files=[],
                             file_type_labels=[],
                             file_type_values=[],
                             category_labels=[],
                             category_values=[])
    
    # Read token counts from CSV
    try:
        with open(TOKEN_COUNTS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                file_path = row['File']
                tokens = int(row['Token Count'])
                file_type = file_path.split('.')[-1] if '.' in file_path else 'unknown'
                category = file_path.split('/')[0] if '/' in file_path else 'unknown'
                
                token_data.append({
                    'path': file_path,
                    'tokens': tokens,
                    'file_type': file_type,
                    'category': category
                })
    except Exception as e:
        return f"Error reading token counts: {str(e)}", 500
    
    # Calculate statistics
    total_tokens = sum(item['tokens'] for item in token_data)
    avg_tokens = total_tokens / len(token_data) if token_data else 0
    max_tokens = max((item['tokens'] for item in token_data), default=0)
    
    # Get top files by token count
    top_files = sorted(token_data, key=lambda x: x['tokens'], reverse=True)[:10]
    
    # Calculate file type distribution
    file_type_counts = {}
    for item in token_data:
        file_type = item['file_type']
        if file_type not in file_type_counts:
            file_type_counts[file_type] = 0
        file_type_counts[file_type] += item['tokens']
    
    file_type_labels = list(file_type_counts.keys())
    file_type_values = [file_type_counts[label] for label in file_type_labels]
    
    # Calculate category distribution
    category_counts = {}
    for item in token_data:
        category = item['category']
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += item['tokens']
    
    # Sort categories by token count
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    category_labels = [item[0] for item in sorted_categories]
    category_values = [item[1] for item in sorted_categories]
    
    return render_template('token_dashboard.html', 
                         token_data=token_data,
                         total_tokens=total_tokens,
                         avg_tokens=avg_tokens,
                         max_tokens=max_tokens,
                         top_files=top_files,
                         file_type_labels=file_type_labels,
                         file_type_values=file_type_values,
                         category_labels=category_labels,
                         category_values=category_values)


@app.route('/profile')
def view_profile():
    """Display the psychological profile in a modern format."""
    try:
        if not PROFILE_FILE.exists():
            return render_template('profile_viewer.html', 
                                profile_html="<p>Profile file not found.</p>",
                                error=True)
        
        # Read the markdown file
        with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        profile_html = markdown.markdown(md_content, extensions=['extra', 'toc'])
        
        return render_template('profile_viewer.html', 
                             profile_html=profile_html,
                             error=False)
    except Exception as e:
        return render_template('profile_viewer.html',
                             profile_html=f"<p>Error loading profile: {str(e)}</p>",
                             error=True)


@app.route('/filter-data')
def filter_data():
    """Filter data from data folder to filtered_data folder."""
    # Check data availability
    data_status = data_handler.check_data_availability()
    if not data_status["data_available"]:
        return redirect(url_for('index'))
    
    # Filter data
    result = data_handler.filter_data()
    
    if result["success"]:
        return render_template('filter_result.html',
                             result=result,
                             success=True)
    else:
        return render_template('filter_result.html',
                             result=result,
                             success=False)

@app.route('/generate-profile')
def generate_profile():
    """Generate psychological profile."""
    # Check data availability
    data_status = data_handler.check_data_availability()
    if not data_status["filtered_data_available"]:
        return redirect(url_for('index'))
    
    # Check if OPENROUTER_API_KEY is set
    if not os.environ.get("OPENROUTER_API_KEY"):
        return render_template('generate_profile.html',
                             error="OPENROUTER_API_KEY environment variable not set",
                             success=False)
    
    try:
        # Run generate_profile.py script
        script_path = BASE_DIR / "generate_profile.py"
        subprocess.Popen([sys.executable, str(script_path)])
        
        return render_template('generate_profile.html',
                             success=True)
    except Exception as e:
        return render_template('generate_profile.html',
                             error=str(e),
                             success=False)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
