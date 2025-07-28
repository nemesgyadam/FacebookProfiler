"""
copy_filtered_data.py

Copy JSON files marked as 'True' in results.csv to data_filtered folder,
preserving the original folder structure.
"""
from pathlib import Path
import pandas as pd
import shutil
from typing import List


def copy_filtered_files(results_csv: Path, source_dir: Path, target_dir: Path) -> None:
    """Copy files marked as True to target directory preserving structure."""
    
    # Read results CSV
    df = pd.read_csv(results_csv)
    print(f"Total files in CSV: {len(df)}")
    print(f"Classifications: {df['classification'].value_counts().to_dict()}")
    
    # Filter for True files (handle both string and boolean)
    true_files = df[df['classification'].astype(str).str.strip() == 'True']['file_path'].tolist()
    
    print(f"Found {len(true_files)} files marked as True")
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(exist_ok=True)
    
    copied_count = 0
    for file_path in true_files:
        source_file = source_dir / file_path
        target_file = target_dir / file_path
        
        if source_file.exists():
            # Create parent directories in target
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_file, target_file)
            print(f"Copied: {file_path}")
            copied_count += 1
        else:
            print(f"Warning: Source file not found: {source_file}")
    
    print(f"\nCopied {copied_count} files to {target_dir}")


def main() -> None:
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    results_csv = project_root / "results.csv"
    source_dir = project_root
    target_dir = project_root / "data_filtered"
    
    if not results_csv.exists():
        print(f"Results CSV not found: {results_csv}")
        return
    
    copy_filtered_files(results_csv, source_dir, target_dir)


if __name__ == "__main__":
    main()
