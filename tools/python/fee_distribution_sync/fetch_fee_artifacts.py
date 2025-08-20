import sys
import json
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional


ALLOCATOR_REPO_BASE = "https://raw.githubusercontent.com/BalancerMaxis/protocol_fee_allocator_v2/refs/heads/biweekly-runs"
MULTISIG_OPS_ROOT = Path(__file__).parent.parent.parent.parent


ARTIFACT_PATHS = {
    "fees": "fee_allocator/fees_collected/{version}_fees_{date_start}_{date_end}.json",
    "incentives": "fee_allocator/allocations/incentives/{version}_incentives_{date_start}_{date_end}.csv",
    "bribes": "fee_allocator/allocations/output_for_msig/{version}_bribes_{date_end}.csv",
    "noncore": "fee_allocator/allocations/noncore/{version}_noncore_{date_start}_{date_end}.csv",
    "partner": "fee_allocator/allocations/partner/{version}_partner_{date_start}_{date_end}.csv",
    "alliance": "fee_allocator/allocations/alliance/{version}_alliance_{date_start}_{date_end}.csv",
}

MAIN_PAYLOAD_PATH = "fee_allocator/payloads/{date_end}.json"


def get_latest_fee_dates() -> Tuple[str, str]:
    api_url = "https://api.github.com/repos/BalancerMaxis/protocol_fee_allocator_v2/pulls"
    params = {"state": "closed", "per_page": 10, "sort": "updated", "direction": "desc"}
    
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    
    prs = response.json()
    
    for pr in prs:
        if pr.get("merged_at") and "Biweekly Fee Report" in pr.get("title", ""):
            title = pr["title"]
            if "ending" in title:
                end_date_str = title.split("ending")[-1].strip()
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                    start_date = end_date - timedelta(days=14)
                    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue
    
    raise ValueError("Could not find recent merged fee report PR. Please provide dates manually.")


def fetch_file(url: str) -> Optional[bytes]:
    print(f"Fetching: {url}")
    response = requests.get(url)
    if response.status_code == 404:
        print(f"  File not found (404), skipping")
        return None
    response.raise_for_status()
    return response.content


def save_file(content: Optional[bytes], path: Path):
    if content is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    print(f"  Saved to: {path}")


def fetch_and_save_artifacts(start_date: str, end_date: str, skip_existing: bool = True):
    target_dir = MULTISIG_OPS_ROOT / "MaxiOps" / "feeDistributions" / end_date
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nFetching artifacts for period {start_date} to {end_date}")
    print(f"Target directory: {target_dir}")
    print(f"Skip existing files: {skip_existing}\n")
    
    files_fetched = []
    files_skipped = []
    
    # Fetch main payload file
    filename = f"{end_date}.json"
    file_path = target_dir / filename
    
    # Skip if file already exists
    if skip_existing and file_path.exists():
        print(f"Skipping existing file: {filename}")
        files_skipped.append(filename)
    else:
        url = f"{ALLOCATOR_REPO_BASE}/{MAIN_PAYLOAD_PATH.format(date_end=end_date)}"
        content = fetch_file(url)
        if content:
            save_file(content, file_path)
            files_fetched.append(filename)
    
    # Fetch v2 and v3 artifact files
    for version in ["v2", "v3"]:
        version_dir = target_dir / version
        
        for file_type, path_template in ARTIFACT_PATHS.items():
            # Build the URL with version and dates
            path = path_template.format(
                version=version,
                date_start=start_date,
                date_end=end_date
            )
            url = f"{ALLOCATOR_REPO_BASE}/{path}"
            
            # Build filename
            if "date_start" in path_template:
                filename = f"{version}_{file_type}_{start_date}_{end_date}"
            else:
                filename = f"{version}_{file_type}_{end_date}"
            
            # Add appropriate extension
            if file_type == "fees":
                filename += ".json"
            else:
                filename += ".csv"
            
            file_path = version_dir / filename
            
            # Skip if file already exists
            if skip_existing and file_path.exists():
                print(f"Skipping existing file: {version}/{filename}")
                files_skipped.append(f"{version}/{filename}")
                continue
            
            content = fetch_file(url)
            import time
            time.sleep(1)
            if content:
                save_file(content, file_path)
                files_fetched.append(f"{version}/{filename}")
    
    print(f"\n✅ Successfully fetched {len(files_fetched)} new files")
    if files_skipped:
        print(f"📁 Skipped {len(files_skipped)} existing files")
    
    return files_fetched, files_skipped


def check_existing_distribution(end_date: str) -> bool:
    """Check if we already have a distribution for this date."""
    target_dir = MULTISIG_OPS_ROOT / "MaxiOps" / "feeDistributions" / end_date
    
    # Check if directory exists and has the main files
    if target_dir.exists():
        main_json = target_dir / f"{end_date}.json"
        if main_json.exists():
            return True
    
    # Also check for open PRs with this date
    api_url = "https://api.github.com/repos/BalancerMaxis/multisig-ops/pulls"
    params = {"state": "open", "per_page": 30}
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        prs = response.json()
        
        for pr in prs:
            title = pr.get("title", "")
            if f"Fee Distribution Artifacts - {end_date}" in title:
                print(f"Found existing open PR for {end_date}: #{pr['number']}")
                return True
    except Exception as e:
        print(f"Warning: Could not check for open PRs: {e}")
    
    return False


def main():
    parser = argparse.ArgumentParser(description="Fetch fee distribution artifacts")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--auto", action="store_true", 
                        help="Automatically detect dates from latest merged PR")
    parser.add_argument("--check-existing", action="store_true",
                        help="Skip if distribution already exists")
    parser.add_argument("--force", action="store_true",
                        help="Force re-fetch all files even if they exist")
    
    args = parser.parse_args()
    
    if args.auto:
        try:
            start_date, end_date = get_latest_fee_dates()
            print(f"Auto-detected dates: {start_date} to {end_date}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.start_date and args.end_date:
        start_date = args.start_date
        end_date = args.end_date
    else:
        print("Error: Please provide either --auto flag or both --start-date and --end-date")
        sys.exit(1)
    
    # Validate date format
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        sys.exit(1)
    
    # Check if we already have this distribution
    if args.check_existing:
        if check_existing_distribution(end_date):
            print(f"\n✅ Distribution for {end_date} already exists or PR is open. Skipping.")
            # Create an empty summary to indicate no action needed
            summary = {
                "start_date": start_date,
                "end_date": end_date,
                "files_fetched": [],
                "target_directory": f"MaxiOps/feeDistributions/{end_date}",
                "skipped": True,
                "reason": "Distribution already exists"
            }
            with open("fetch_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            sys.exit(0)
    
    # Fetch and save artifacts
    skip_existing = not args.force  # Skip existing files unless --force is used
    files_fetched, files_skipped = fetch_and_save_artifacts(start_date, end_date, skip_existing)
    
    # Write a summary for the workflow
    summary = {
        "start_date": start_date,
        "end_date": end_date,
        "files_fetched": files_fetched,
        "files_skipped": files_skipped,
        "target_directory": f"MaxiOps/feeDistributions/{end_date}"
    }
    
    with open("fetch_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSummary written to fetch_summary.json")


if __name__ == "__main__":
    main()