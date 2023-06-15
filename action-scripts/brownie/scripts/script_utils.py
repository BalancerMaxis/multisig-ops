import json
import os
from json import JSONDecodeError

import requests
from brownie import Contract
from prettytable import PrettyTable

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
                    payload['file_name'] = filename
                except JSONDecodeError:
                    print(f"{filename} is not proper json")
                    continue
                if isinstance(payload, dict) is False:
                    print(f"{filename} json is not a dict")
                    continue
                if "transactions" not in payload.keys():
                    print(f"{filename} json deos not contain a list of transactions")
                    continue
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


def convert_output_into_table(outputs: list[dict], header: list[str]) -> str:
    """
    Converts list of dicts into a pretty table
    """
    table = PrettyTable(header)
    for dict_ in outputs:
        table.add_row(list(dict_.values()))
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
    file_report += "```\n"
    file_report += convert_output_into_table(
        transactions, list(transactions[0].keys())
    )
    file_report += "\n```\n"
    return file_report
