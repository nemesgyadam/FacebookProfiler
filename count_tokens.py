"""Count tokens in markdown and JSON files using Google Gemini API."""

import os
from pathlib import Path
from typing import Dict, List, Tuple
from google import genai


def get_files_to_process(directory: str) -> List[Path]:
    """Get all .md and .json files in the directory."""
    data_dir = Path(directory)
    files = []
    
    for ext in ['*.md', '*.json']:
        files.extend(data_dir.rglob(ext))
    
    return sorted(files)


def read_file_content(file_path: Path) -> str:
    """Read file content with proper encoding handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()


def count_tokens_for_file(client: genai.Client, content: str, model: str = "gemini-2.5-flash") -> int:
    """Count tokens for given content using Gemini API."""
    try:
        response = client.models.count_tokens(model=model, contents=content)
        # Extract the token count from the CountTokensResponse object
        return response.total_tokens
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return 0


def main() -> None:
    """Main function to count tokens for all files."""
    # Initialize Gemini client
    client = genai.Client()
    
    # Get files to process
    data_filtered_dir = "data_filtered"
    files = get_files_to_process(data_filtered_dir)
    
    print(f"Found {len(files)} files to process\n")
    
    total_tokens = 0
    results: List[Tuple[str, int]] = []
    
    for file_path in files:
        print(f"Processing: {file_path}")
        
        # Read file content
        content = read_file_content(file_path)
        
        # Count tokens
        token_count = count_tokens_for_file(client, content)
        
        # Store results
        relative_path = str(file_path.relative_to(Path(data_filtered_dir)))
        results.append((relative_path, token_count))
        total_tokens += token_count
        
        print(f"  Tokens: {token_count:,}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total files processed: {len(files)}")
    print(f"Total tokens: {total_tokens:,}")
    print(f"Average tokens per file: {total_tokens/len(files):.1f}")
    
    # Print top 10 largest files by token count
    print(f"\nTop 10 files by token count:")
    print("-" * 60)
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    for i, (file_path, tokens) in enumerate(sorted_results[:10], 1):
        print(f"{i:2d}. {file_path:<45} {tokens:>8,} tokens")
    
    # Save detailed results to CSV
    import csv
    with open('token_counts.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['File', 'Token Count'])
        writer.writerows(sorted_results)
    
    print(f"\nDetailed results saved to 'token_counts.csv'")


if __name__ == "__main__":
    main()
