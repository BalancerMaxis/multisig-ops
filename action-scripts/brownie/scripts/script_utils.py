import json
import os
from json import JSONDecodeError

import requests
from brownie import Contract
from prettytable import PrettyTable
import re

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

NA = "N/A"
NOT_FOUND = "Not Found"
POOL_ID_CUSTOM_FALLBACK = "Custom"
BIPS_PRECISION = 1e16


def get_changed_files() -> list[dict]:
    """
    Parses given GH repo and PR number to return a list of dicts of changed files

    Each file should be a valid json with a list of transactions

    Returns only BIPs
    """
    github_repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    api_url = f'https://api.github.com/repos/{github_repo}/pulls/{pr_number}/files'
    response = requests.get(api_url)
    pr_file_data = json.loads(response.text)
    changed_files = []
    for file_json in pr_file_data:
        filename = (file_json['filename'])
        if "BIPs/" in filename and filename.endswith(".json"):
            # Check if file exists first
            if os.path.isfile(f"{ROOT_DIR}/{filename}") is False:
                print(f"{filename} does not exist")
                continue
            # Validate that file is a valid json
            with open(f"{ROOT_DIR}/{filename}", "r") as json_data:
                try:
                    payload = json.load(json_data)
                except JSONDecodeError:
                    print(f"{filename} is not proper json")
                    continue
                if isinstance(payload, dict) is False:
                    print(f"{filename} json is not a dict")
                    continue
                if "transactions" not in payload.keys():
                    print(f"{filename} json deos not contain a list of transactions")
                    continue
            payload['file_name'] = filename
            changed_files.append(payload)
    return changed_files


def get_pool_info(pool_address) -> tuple[str, str, str, str, str, str]:
    """
    Returns a tuple of pool info
    """
    pool = Contract.from_abi(
        name="IBalPool", address=pool_address, abi=json.load(open("abis/IBalPool.json", "r"))
    )
    try:
        (a_factor, ramp, divisor) = pool.getAmplificationParameter()
        a_factor = int(a_factor / divisor)
        if not isinstance(a_factor, int):
            a_factor = NA
    except Exception:
        a_factor = NA
    name = pool.name()
    symbol = pool.symbol()
    try:
        pool_id = str(pool.getPoolId())
    except Exception:
        pool_id = POOL_ID_CUSTOM_FALLBACK
    try:
        fee = pool.getSwapFeePercentage() / BIPS_PRECISION
    except Exception:
        fee = NOT_FOUND
    if pool.totalSupply == 0:
        symbol = f"WARN: {symbol} no initjoin"
    return name, symbol, pool_id, pool.address, a_factor, fee


def convert_output_into_table(outputs: list[dict]) -> str:
    """
    Converts list of dicts into a pretty table
    """
    # Headers without "chain"
    header = [k for k in outputs[0].keys() if k != "chain"]
    table = PrettyTable(header)
    for dict_ in outputs:
        # Create a dict comprehension to include all keys and values except "chain"
        # As we don't want to display chain in the table
        dict_filtered = {k: v for k, v in dict_.items() if k != "chain"}
        table.add_row(list(dict_filtered.values()))
    table.align["pool_name"] = "l"
    table.align["function"] = "l"
    table.align["style"] = "l"
    return str(table)


def format_into_report(file: dict, transactions: list[dict]) -> str:
    """
    Formats a list of transactions into a report that can be posted as a comment on GH PR
    """
    file_report = f"File name: {file['file_name']}\n"
    file_report += f"COMMIT: `{os.getenv('COMMIT_SHA', 'N/A')}`\n"
    # Format chains and remove "-main" from suffix of chain name
    chains = set(
        map(
            lambda chain: chain.replace("-main", ""),
            [transaction['chain'] for transaction in transactions]
        )
    )
    file_report += f"CHAIN(S): `{', '.join(chains)}`\n"
    file_report += "```\n"
    file_report += convert_output_into_table(transactions)
    file_report += "\n```\n"
    return file_report


def merge_files(
        added_gauges: dict[str, str],
        removed_gauges: dict[str, str],
        transfers: dict[str, str],
) -> dict[str, str]:
    """
    Function that merges two dictionaries into one.

    Extend with more dictionaries if needed.

    Say we have two dictionaries:
    added_gauges = {
        "file1.json": "report1",
        "file2.json": "report2",
    }
    removed_gauges = {
        "file1.json": "report3",
        "file3.json": "report4",
    }
    Then the result of merging will be:
    merged_dict = {
        "file1.json": "report1report3",
        "file2.json": "report2",
        "file3.json": "report4",
    }
    """
    merged_dict = {}
    for key in added_gauges.keys() | removed_gauges.keys() | transfers.keys():
        merged_dict[key] = "".join([
            added_gauges.get(key, ""),
            removed_gauges.get(key, ""),
            transfers.get(key, ""),
        ])
    return merged_dict

def get_bip_number(path: str) -> str:
    """
    Function that gets a BIP number from a file name by searching BIP-### pattterns.
    Will throw a ValueError if exactly 1 result is not found, otherwise return a result like BIP-###
    """
    # Define the regular expression pattern
    pattern = r"BIP-\d{3,}"
    # Search for the pattern in the given path
    matches = re.findall(pattern, path)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        print(f"No BIP number found in file: {path}")
        return
    else:
        raise ValueError(f"More than 1 BIP number in file path found: {matches}, {path}")



def add_bip_number_data(files: list[dict]):
    """
    Function expects a list of payload dicts, with file_name included at the top level.
    It will add bip_number from the file to the top level of the payload as well as to each transaction.
    The function will throw an error if a single BIP number can not be found for each listed payload.
    """
    for payload in files:
        new_tx_list = []
        file_name = payload["file_name"]
        print(f"Adding BIP data to {file_name}")
        assert isinstance(file_name, str), f"no filename in payload data. {payload}"
        bip_number = get_bip_number(file_name)
        if bip_number is None:
            continue
        payload["meta"]["bip_number"] = bip_number
        for tx in payload["transactions"]:
            tx["bip_number"] = bip_number
        with open(file_name, "w") as f:
            json.dump(payload, f, indent=2)




