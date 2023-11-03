import argparse
import json
import os
import re
from collections import defaultdict
from json import JSONDecodeError
from typing import Optional
from web3 import Web3
from bal_addresses import AddrBook

ADDRESSES_MAINNET = AddrBook("mainnet").reversebook
ADDRESSES_POLYGON = AddrBook("polygon").reversebook
ADDRESSES_ARBITRUM = AddrBook("arbitrum").reversebook
ADDRESSES_AVALANCHE = AddrBook("avalanche").reversebook
ADDRESSES_OPTIMISM = AddrBook("optimism").reversebook
ADDRESSES_GNOSIS = AddrBook("gnosis").reversebook
ADDRESSES_ZKEVM = AddrBook("zkevm").reversebook
ADDRESSES_BASE = AddrBook("base").reversebook

# Merge all addresses into one dictionary
ADDRESSES = {**ADDRESSES_MAINNET, **ADDRESSES_POLYGON, **ADDRESSES_ARBITRUM, **ADDRESSES_AVALANCHE,
             **ADDRESSES_OPTIMISM, **ADDRESSES_GNOSIS, **ADDRESSES_ZKEVM, **ADDRESSES_BASE}

# Initialize the parser
parser = argparse.ArgumentParser()
parser.add_argument("--target", help="Target directory to merge BIPs from")

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

IGNORED_DIRECTORIES = ["examples", "rejected", "batched", "proposed"]
# Place your BIPs json into this directory under BIPs/<TARGET_DIR_WITH_BIPS>
TARGET_DIR_WITH_BIPS = "00merging"
TEMPLATE_PATH = os.path.dirname(
    os.path.abspath(__file__)) + "/tx_builder_templates/l2_checkpointer_gauge_add.json"


class NoMsigAddress(Exception):
    pass


class NoChainSpecified(Exception):
    pass


class AddressNotFound(Exception):
    pass


def extract_bip_number(bip_file: dict) -> Optional[str]:
    """
    Extracts BIP number from file path or from transactions metadata
    """
    bip = None
    # First, try to exctract BIP from file path
    if bip_file.get('file_name') is not None:
        bip_match = re.search(r"BIP-?\d+", bip_file["file_name"])
        bip = bip_match.group(0) if bip_match else None

    # If no BIP in file path, try to extract it from transactions metadata
    if not bip:
        for tx in bip_file['transactions']:
            if tx.get('meta', {}).get('bip') not in [None, "N/A"]:
                bip = tx['meta']['bip']
                break
    return bip or "N/A"


def _parse_bip_json(file_path: str, chain: int) -> Optional[dict]:
    """
    In case file was created within given date bounds and for given chain -
    parse it and return the data.

    Also perform various validations on the file.
    """
    # Check if the file is a json file
    if not file_path.endswith(".json"):
        return None
    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
            if not isinstance(data, dict):
                return None
            data['file_name'] = file_path
    except JSONDecodeError:
        return None

    # VALIDATIONS. Everything should fail here if the file is not valid
    # Check if the file is a dictionary, not a list
    if not isinstance(data, dict) or not data.get('transactions'):
        return None

    # Check if chain id is the same as the one we are looking for
    if not data.get("chainId"):
        raise NoChainSpecified(f"No chain id found in file: {file_path}")

    msig = data['meta'].get('createdFromSafeAddress') or data['meta'].get('createFromSafeAddress')
    if not msig or not isinstance(msig, str):
        raise NoMsigAddress(f"No msig address found in file: {file_path}, or it is not a string")

    # Check if msig address is in the address book
    if Web3.toChecksumAddress(msig) not in ADDRESSES:
        raise AddressNotFound(
            f"msig address {msig} not found in address book in file: {file_path}"
        )

    if int(data["chainId"]) == int(chain):
        return data


def _write_checkpointer_json(output_file_path: str, gauges_by_chain: dict):
    for chain, gauges in gauges_by_chain.items():
        gauges_by_chain[chain] = str(gauges).replace("'", "")
    with open(output_file_path, "w") as l2_payload_file:
        json.dump(gauges_by_chain, l2_payload_file, indent=2)


# Example how to run: `python action-scripts/merge_pr_jsons.py --target 2023-W23`
# Note: if you need to merge multiple directories, you can use old multi_merge_pr_jsons.py script
def main():
    directory = parser.parse_args().target
    if not directory:
        raise ValueError("No directory was passed in as argument")
    print(f"Directory to parse:{directory}")
    gauge_lists_by_chain = defaultdict(list)

    match = re.search(r'(\d{4})-W(\d{1,2})', directory)
    if not match:
        raise ValueError("Directory name is not in the correct format. Consider using YYYY-WW")
    year, week = match.groups()
    # get root directory of the project:
    # To do this you need to go up 2 levels from the current file
    # For instance, to get to the project root from: multisig-ops/action-scripts/merge_pr_jsons.py
    # You need to jump up two steps with os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_name_batched = f"BIPs/00batched/{year}-W{week}"
    dir_name_batched_full = os.path.join(root_dir, dir_name_batched)

    files_to_parse = []
    target_files = defaultdict(list)
    # If directory doesn't exist, raise an error
    if not os.path.exists(os.path.join(root_dir, directory)):
        raise ValueError(f"Directory {directory} does not exist. Pass correct directory name")
    # Parse each directory for underlying files
    for root, __, files in os.walk(os.path.join(root_dir, directory)):
        for file in files:
            # Skip non json files
            if not file.endswith(".json"):
                continue
            files_to_parse.append(os.path.join(root, file))

    # Walk through all nested directories in BIPs
    for file in files_to_parse:
        # Process files that are lying flat in BIPs directory
        for chain_name, chain_id in AddrBook.chain_ids_by_name.items():
            data = _parse_bip_json(
                os.path.join(root_dir, file), chain=chain_id
            )
            if data:
                # Add the file to the list of files to be merged
                target_files[str(chain_id)].append(data)

    # Now we have a list of files to be merged, let's merge them and save to files
    # Create the directory if it does not exist in root directory
    if not os.path.exists(dir_name_batched_full):
        os.mkdir(dir_name_batched_full)

    # Now we need to group files by safe address as well
    for chain_id, files in target_files.items():
        # Group files by safe address
        grouped_files = defaultdict(list)
        for file in files:
            safe_address = file["meta"].get("createdFromSafeAddress") or file["meta"].get(
                "createFromSafeAddress"
            )
            grouped_files[safe_address].append(file)

        # Now we have a list of files grouped by safe address, let's merge them and save to files
        for safe_address, fs in grouped_files.items():
            # Merge all the files into one
            result = base_json
            result['meta']['createdFromSafeAddress'] = safe_address
            result['chainId'] = chain_id
            result["transactions"] = []
            for file in fs:
                #  Check for gauge adds and generate checkpoint list
                for tx in file["transactions"]:
                    tx["meta"] = {
                        "tx_index": file["transactions"].index(tx),
                        "origin_file_name": file['file_name'],
                        "bip_number": extract_bip_number(file),
                    }
                    if "contractMethod" in tx.keys():
                        if tx["contractMethod"]["name"] == "addGauge":
                            try:
                                gauge_chain = tx["contractInputsValues"]["gaugeType"]
                                if gauge_chain != "Ethereum":
                                    gauge_lists_by_chain[gauge_chain].append(
                                        tx["contractInputsValues"]["gauge"])
                            except KeyError:
                                print(
                                    f"Skipping checkpointer add for addGauge tx "
                                    f"as it doesn't have expected inputs:\n---\n "
                                    f"{tx['contractInputsValues']}"
                                )
                result["transactions"] += file["transactions"]
            # Save the result to file
            file_name = f"{chain_id}-{safe_address}.json"
            file_path = os.path.join(dir_name_batched_full, file_name)
            with open(file_path, "w") as new_file:
                json.dump(result, new_file, indent=2)
    if gauge_lists_by_chain:
        _write_checkpointer_json(f"{dir_name_batched_full}/checkpointer_gauges_by_chain.json",
                                 gauge_lists_by_chain)


if __name__ == "__main__":
    main()
