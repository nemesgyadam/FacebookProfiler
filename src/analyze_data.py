"""analyze_data.py

Use GPT-4o-mini to classify JSON files in data/ folder for psychological profiling.
Classify as True/False/Maybe based on psychological profile indicators.
"""
from pathlib import Path
import json
import pandas as pd
import openai
from typing import List, Dict
import os


def load_json_file(path: Path) -> str:
    """Load and return JSON file content as string."""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            # Truncate if too large (GPT has token limits)
            content = json.dumps(data, indent=2)
            if len(content) > 8000:  # Conservative limit
                content = content[:8000] + "...[truncated]"
            return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


def classify_with_gpt(content: str, file_path: str) -> str:
    """Use GPT-4o-mini to classify file content."""
    prompt = f"""Analyze this JSON file content to determine if it contains information useful for creating a psychological profile of a user.

File: {file_path}
Content:
{content}

Classify as:
- "True" if it contains information about user preferences, likes, behavior, interests, or personality traits
- "False" if it contains only technical data, metadata, or no useful psychological information
- "Maybe" if uncertain or contains mixed content

Respond with only: True, False, or Maybe"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        result = response.choices[0].message.content.strip()
        return result if result in ["True", "False", "Maybe"] else "Maybe"
    except Exception as e:
        print(f"Error classifying {file_path}: {str(e)}")
        return "Maybe"


def analyze_json_files(data_dir: Path) -> List[Dict[str, str]]:
    """Analyze only JSON files using GPT-4o-mini."""
    results: List[Dict[str, str]] = []
    json_files = list(data_dir.rglob("*.json"))
    
    print(f"Found {len(json_files)} JSON files to analyze...")
    
    for i, path in enumerate(json_files, 1):
        print(f"Processing {i}/{len(json_files)}: {path.name}")
        content = load_json_file(path)
        classification = classify_with_gpt(content, str(path))
        results.append({
            "file_path": str(path.relative_to(data_dir.parent)),
            "classification": classification
        })
    
    return results


def main() -> None:
    """Main entry point."""
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    root = Path(__file__).parent.parent / "data"
    if not root.exists():
        print(f"Data directory not found: {root}")
        return
    
    results = analyze_json_files(root)
    df = pd.DataFrame(results)
    out_path = Path(__file__).parent.parent / "results.csv"
    df.to_csv(out_path, index=False)
    
    print(f"\nAnalysis complete. Results saved to {out_path}")
    print(f"Processed {len(results)} JSON files")
    print(f"Classifications: {df['classification'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
