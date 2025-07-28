"""
Simple API server to handle OpenRouter API calls for the Facebook Profile Analyzer.
This avoids CORS issues when calling OpenRouter API directly from the browser.
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from generate_profile import generate_profile, read_prompt

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/generate-profile', methods=['POST'])
def api_generate_profile():
    """
    API endpoint to generate a psychological profile from Facebook data.
    Expects a JSON payload with the processed Facebook data.
    """
    try:
        # Get data from request
        request_data = request.get_json()
        if not request_data or 'data' not in request_data:
            return jsonify({'error': 'Missing data in request'}), 400
        
        # Get the prompt
        try:
            prompt = read_prompt()
        except Exception as e:
            return jsonify({'error': f'Failed to read prompt: {str(e)}'}), 500
        
        # Generate profile
        profile = generate_profile(prompt, request_data['data'])
        
        # Return the generated profile
        return jsonify({
            'success': True,
            'profile': profile,
            'stats': {
                'profileLength': len(profile),
                'wordCount': len(profile.split())
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('REACT_PORT', 8080))
    
    print(f"Starting API server on port {port}...")
    print("API endpoint: /api/generate-profile")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
