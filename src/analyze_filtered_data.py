"""
analyze_filtered_data.py

Analyze each JSON file in data_filtered using GPT-4o-mini and generate 
detailed Markdown summaries for psychological profiling and mental health analysis.
"""
from pathlib import Path
import json
import openai
import os
from typing import Dict, Any


def load_json_content(json_path: Path) -> str:
    """Load JSON file and return formatted content."""
    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Pretty format the JSON for analysis
        content = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Truncate if too large for GPT context
        if len(content) > 12000:
            content = content[:12000] + "\n\n...[Content truncated for analysis]"
            
        return content
    except Exception as e:
        return f"Error loading JSON: {str(e)}"


def analyze_json_with_gpt(content: str, file_path: str) -> str:
    """Use GPT-4o-mini to analyze JSON content for psychological profiling."""
    
    prompt = f"""Analyze this Facebook data JSON file for psychological profiling and mental health insights.

FILE: {file_path}

CONTENT:
{content}

Please provide a comprehensive analysis in Markdown format covering:

# {Path(file_path).stem} Analysis

## Content Overview
- What type of Facebook data is this?
- What time period does it cover?
- How much data is present?

## Data Structure
- Key fields and their meanings
- Data organization and patterns
- Notable technical aspects

## Psychological Insights
- What does this data reveal about the user's:
  - Behavioral patterns
  - Preferences and interests  
  - Social interactions
  - Digital habits
  - Emotional indicators
- Specific examples from the data

## Mental Health & Trauma Analysis Potential
- How could this data help understand:
  - Mental health patterns
  - Stress indicators
  - Social support systems
  - Coping mechanisms
  - Triggers or trauma responses
- Therapeutic insights available

## Key Findings
- Most important discoveries
- Patterns worth investigating further
- Red flags or concerning patterns
- Positive indicators

## Recommendations for Profile Building
- How to integrate this data into psychological profile
- Connections to explore with other data sources
- Areas needing deeper analysis

Focus on actionable psychological insights that could aid in mental health improvement and trauma healing."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"# Analysis Error\n\nFailed to analyze {file_path}: {str(e)}"


def process_filtered_data(data_filtered_dir: Path) -> None:
    """Process all JSON files in data_filtered directory."""
    
    json_files = list(data_filtered_dir.rglob("*.json"))
    
    if not json_files:
        print("No JSON files found in data_filtered directory")
        return
    
    print(f"Found {len(json_files)} JSON files to analyze...")
    
    for i, json_path in enumerate(json_files, 1):
        print(f"Processing {i}/{len(json_files)}: {json_path.name}")
        
        # Create markdown file path with same name
        md_path = json_path.with_suffix('.md')
        
        # Skip if MD file already exists
        if md_path.exists():
            print(f"  ⏭ Skipped (already exists): {md_path.name}")
            continue
        
        # Load JSON content
        content = load_json_content(json_path)
        
        # Analyze with GPT
        analysis = analyze_json_with_gpt(content, str(json_path))
        
        try:
            with md_path.open("w", encoding="utf-8") as f:
                f.write(analysis)
            print(f"  ✓ Created analysis: {md_path.name}")
        except Exception as e:
            print(f"  ✗ Failed to write {md_path.name}: {str(e)}")
    
    print(f"\nCompleted analysis of {len(json_files)} files")


def main() -> None:
    """Main entry point."""
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Find data_filtered directory
    project_root = Path(__file__).parent.parent
    data_filtered_dir = project_root / "data_filtered"
    
    if not data_filtered_dir.exists():
        print(f"data_filtered directory not found: {data_filtered_dir}")
        return
    
    process_filtered_data(data_filtered_dir)


if __name__ == "__main__":
    main()
