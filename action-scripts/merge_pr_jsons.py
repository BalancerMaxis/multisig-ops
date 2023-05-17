import json
import os
from collections import defaultdict
from datetime import datetime
from json import JSONDecodeError
from typing import Optional

base_json = json.loads('''
{
  "version": "1.0",
  "chainId": "",
  "createdAt": 1675891944772,
  "meta": {
    "name": "Transactions Batch",
    "description": "",
    "txBuilderVersion": "1.13.2",
    "createdFromSafeAddress": "",
    "createdFromOwnerAddress": ""
  },
  "transactions": [
  ]
}
''')

CHAIN_IDS = {
    1: "mainnet",
    3: "ropsten",
    42161: "arbitrum",
    100: "gnosis",
    137: "polygon",
    10: "optimism",
}
IGNORED_DIRECTORIES = ["examples", "rejected", "batched", "proposed"]
# Place your BIPs json into this directory under BIPs/<TARGET_DIR_WITH_BIPS>
TARGET_DIR_WITH_BIPS = "00merging"


def _parse_bip_json(file_path: str, chain: int) -> Optional[dict]:
    """
    In case file was created within given date bounds and for given chain -
    parse it and return the data
    """
    # Check if the file is a json file
    if not file_path.endswith(".json"):
        return None
    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
            # Check if the file is a dictionary, not a list
            if not isinstance(data, dict):
                return None
            # Check if chain id is the same as the one we are looking for
            if int(data["chainId"]) == int(chain):
                return data
    except JSONDecodeError:
        return None


# TODO: Feed directories as inputs
def main():
    current_week = datetime.utcnow().strftime("%U")
    current_year = datetime.utcnow().year
    # get root directory of the project:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bips_dir = os.path.join(root_dir, "BIPs")
    dir_with_target_bips = os.path.join(bips_dir, TARGET_DIR_WITH_BIPS)
    if not os.path.exists(dir_with_target_bips):
        raise ValueError(f"Directory {TARGET_DIR_WITH_BIPS} does not exist")
    target_files = defaultdict(list)
    # Walk through BIPs directory and find all the files that were created this week
    for root, __, files in os.walk(dir_with_target_bips):
        # Walk through all nested directories in BIPs
        for file in files:
            # Process files that are lying flat in BIPs directory
            for chain_id, chain_name in CHAIN_IDS.items():
                data = _parse_bip_json(
                    os.path.join(root, file), chain=chain_id
                )
                if data:
                    # Add the file to the list of files to be merged
                    target_files[str(chain_id)].append(data)

    # Now we have a list of files to be merged, let's merge them and save to files
    dir_name_batched = f"BIPs/00batched/{current_year}-{current_week}"
    dir_name_batched_full = os.path.join(root_dir, dir_name_batched)
    # Create the directory if it does not exist in root directory
    if not os.path.exists(dir_name_batched_full):
        os.mkdir(dir_name_batched_full)

    # Now we need to group files by safe address as well
    for chain_id, files in target_files.items():
        # Group files by safe address
        grouped_files = defaultdict(list)
        for file in files:
            safe_address = file["meta"]["createdFromSafeAddress"]
            if not safe_address:
                safe_address = file["meta"]["createFromSafeAddress"]
            grouped_files[safe_address].append(file)

        # Now we have a list of files grouped by safe address, let's merge them and save to files
        for safe_address, files in grouped_files.items():
            # Merge all the files into one
            result = base_json
            result['meta']['createdFromSafeAddress'] = safe_address
            result['chainId'] = chain_id
            result["transactions"] = []
            for file in files:
                result["transactions"] += file["transactions"]
            # Save the result to file
            file_name = f"{chain_id}-{safe_address}.json"
            file_path = os.path.join(dir_name_batched_full, file_name)
            with open(file_path, "w") as new_file:
                json.dump(result, new_file, indent=2)


if __name__ == "__main__":
    main()
