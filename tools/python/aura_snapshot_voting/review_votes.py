import pandas as pd
import glob
import os
import argparse
from pathlib import Path

def find_project_root(current_path=None):
    anchor_file = "multisigs.md"
    if current_path is None:
        current_path = Path(__file__).resolve().parent
    if (current_path / anchor_file).exists():
        return current_path
    parent = current_path.parent
    if parent == current_path:
        raise FileNotFoundError("Project root not found")
    return find_project_root(parent)

def review_votes(week_string):
    year, week = week_string.split("-")
    project_root = find_project_root()
    base_path = project_root / "MaxiOps/vlaura_voting"
    voting_dir = base_path / str(year) / str(week)
    input_dir = voting_dir / "input"
    
    csv_files = glob.glob(str(input_dir / "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")
    
    csv_file = csv_files[0]
    vote_df = pd.read_csv(csv_file)
    
    # Perform checks
    total_allocation = vote_df["Allocation %"].str.rstrip("%").astype(float).sum()
    allocation_check = abs(total_allocation - 100) < 0.001
    
    # Generate report
    report = f"""## vLAURA Votes Review

CSV file: `{os.path.relpath(csv_file, project_root)}`

### Allocation Check
Total allocation: {total_allocation:.2f}%
Passes 100% check: {"Yes" if allocation_check else "No"}

### Vote Summary
{vote_df[["Chain", "Gauge Address", "Allocation %"]].to_string(index=False)}

{"### ✅ All checks passed" if allocation_check else "### ❌ Some checks failed"}
"""
    
    with open("review_output.md", "w") as f:
        f.write(report)
    
    if not allocation_check:
        raise ValueError("Allocation does not sum to 100%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vote review script")
    parser.add_argument(
        "--week-string",
        type=str,
        required=True,
        help="Date that votes are being reviewed. Should be YYYY-W##",
    )
    args = parser.parse_args()
    review_votes(args.week_string)