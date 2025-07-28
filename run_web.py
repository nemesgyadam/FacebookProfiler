#!/usr/bin/env python3
"""
Simple script to run the Facebook Data Browser web interface.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from web.app import app

if __name__ == '__main__':
    print("🚀 Starting Facebook Data Browser...")
    print("📊 Navigate to: http://localhost:5000")
    print("🔍 Use the search box to find specific data")
    print("📁 Click on categories to explore your data")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
