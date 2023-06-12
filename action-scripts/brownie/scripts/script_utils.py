import json
import os
from json import JSONDecodeError

import requests
from brownie import Contract
from prettytable import PrettyTable

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def get_changed_files() -> list[dict]:
    github_repo = "BalancerMaxis/multisig-ops"
    # github_repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = 233
    # pr_number = os.environ["PR_NUMBER"]
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
    pool_abi = json.load(open("abis/IBalPool.json", "r"))
    pool = Contract.from_abi(name="IBalPool", address=pool_address, abi=pool_abi)
    try:
        (a_factor, ramp, divisor) = pool.getAmplificationParameter()
        a_factor = int(a_factor/divisor)
        if not isinstance(a_factor, int):
            a_factor = "N/A"
    except Exception:
        a_factor = "N/A"
    name = pool.name()
    symbol = pool.symbol()
    try:
        poolId = str(pool.getPoolId())
    except Exception:
        poolId = "Custom"
    try:
        fee = pool.getSwapFeePercentage() / 1e16
    except Exception:
        fee = "Not Found"
    if pool.totalSupply ==  0:
        symbol = f"WARN: {symbol} no initjoin"
    return name, symbol, poolId, pool.address, a_factor, fee


def convert_output_into_table(outputs: list[dict], header: list[str]) -> str:
    table = PrettyTable(header)
    for dict_ in outputs:
        table.add_row(list(dict_.values()))
    table.align["pool_name"] = "l"
    table.align["function"] = "l"
    table.align["style"] = "l"
    return str(table)
