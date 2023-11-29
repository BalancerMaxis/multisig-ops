import json
import os
import re
from json import JSONDecodeError
from typing import Optional

import web3
from tabulate import tabulate
from collections import defaultdict
from bal_addresses import AddrBook, BalPermissions
import requests
from brownie import Contract, chain, network
from web3 import Web3

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
    api_url = f"https://api.github.com/repos/{github_repo}/pulls/{pr_number}/files"
    response = requests.get(api_url)
    pr_file_data = json.loads(response.text)
    changed_files = []
    for file_json in pr_file_data:
        filename = file_json["filename"]
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
            payload["file_name"] = filename
            changed_files.append(payload)
    return changed_files


def get_pool_info(
    pool_address,
) -> tuple[str, str, str, str, str, str, list[str], list[str]]:
    """
    Returns a tuple of pool info
    """
    pool = Contract.from_abi(
        name="IBalPool",
        address=pool_address,
        abi=json.load(open("abis/IBalPool.json", "r")),
    )
    chain_name = AddrBook.chain_names_by_id[chain.id]
    book = AddrBook(chain_name)
    vault = Contract.from_abi(
        name="Vault",
        address=book.search_unique("vault/Vault").address,
        abi=json.load(open("abis/IVault.json")),
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
        try:
            ## TWAMM pools
            pool = Contract.from_explorer(pool.address)
            pool_id = str(pool.POOL_ID())
        except Exception:
            pool_id = POOL_ID_CUSTOM_FALLBACK
    try:
        fee = pool.getSwapFeePercentage() / BIPS_PRECISION
    except Exception:
        fee = NOT_FOUND
    try:
        tokens = vault.getPoolTokens(pool_id)[0]
    except Exception:
        tokens = []
    try:
        rate_providers = pool.getRateProviders()
    except Exception:
        rate_providers = []
    if pool.totalSupply == 0:
        symbol = f"WARN: {symbol} no initjoin"

    return name, symbol, pool_id, pool.address, a_factor, fee, tokens, rate_providers


def convert_output_into_table(outputs: list[dict]) -> str:
    """
    Converts list of dicts into a pretty table
    """
    # Headers without "chain"
    header = [k for k in outputs[0].keys() if k != "chain"]
    table = []
    for dict_ in outputs:
        # Create a dict comprehension to include all keys and values except "chain"
        # As we don't want to display chain in the table
        dict_filtered = {k: v for k, v in dict_.items() if k != "chain"}
        table.append(list(dict_filtered.values()))
    return str(tabulate(table, headers=header, tablefmt="grid"))


def format_into_report(
    file: dict,
    transactions: list[dict],
    msig_addr: str,
    chain_id: int,
) -> str:
    """
    Formats a list of transactions into a report that can be posted as a comment on GH PR
    """
    chain_name = AddrBook.chain_names_by_id[chain_id]
    book = AddrBook(chain_name)
    msig_label = book.reversebook.get(
        web3.Web3.toChecksumAddress(msig_addr), "!NOT FOUND"
    )
    file_name = file["file_name"]
    file_report = f"File name: {file_name}\n"
    file_report += f"MULTISIG: `{msig_label} ({msig_addr})`\n"
    file_report += f"MULTISIG CHAIN: `{chain_id}`\n"
    file_report += f"COMMIT: `{os.getenv('COMMIT_SHA', 'N/A')}`\n"
    result = extract_chain_id_and_address_from_filename(file_name)
    print(result)
    if result:
        (chain_id, address) = result
        chain_name = AddrBook.chain_names_by_id[chain_id]
        book = AddrBook(chain_name)
        multisig = book.reversebook.get(
            web3.Web3.toChecksumAddress(address), "!NOT FOUND"
        )
        file_report += f"MERGED PAYLOAD: Chain:{chain_name} ({chain_id}), Multisig: {multisig} ({address})\n"
    # Format chains and remove "-main" from suffix of chain name
    chains = set(
        map(
            lambda chain: chain.replace("-main", ""),
            [transaction["chain"] for transaction in transactions],
        )
    )
    file_report += f"CHAIN(S): `{', '.join(chains)}`\n"
    file_report += "```\n"
    file_report += convert_output_into_table(transactions)
    file_report += "\n```\n"
    return file_report


def extract_chain_id_and_address_from_filename(file_name: str):
    ## TODO set output type can be {int, str} or None
    """
    Grabs a chain_id and multisig address from a payload file name if it is formatted like chain-address.something
    """
    # Define the regular expression pattern to match the desired format
    pattern = r"(\d+)-(0x[0-9a-fA-F]+)"

    # Try to find a match in the input string
    match = re.search(pattern, file_name)
    if match:
        # Extract the chain_id and address from the matched groups
        chain_id = int(match.group(1))
        address = match.group(2)
        return int(chain_id), address
    else:
        # Return None if the pattern does not match the input string
        return None


def get_token_symbol(token_address) -> Optional[str]:
    """
    Try to look up a token symbol on chain and return it if it exists
    """
    try:
        return Contract.from_abi(
            "Token", token_address, json.load(open("abis/ERC20.json"))
        ).symbol()
    except Exception as err:
        print(err)
        return


def prettify_tokens_list(token_addresses: list[str]) -> list[str]:
    """
    Return a list of token addresses and names in string format.
    Uses onchain lookups with brownie, requires you are on the network of the token when run
    """
    results = []
    for token in token_addresses:
        results.append(f"{get_token_symbol(token)}({token})")
    return results


def prettify_contract_inputs_values(chain: str, contracts_inputs_values: dict) -> dict:
    """
    Accepts contractInputsValues dict with key of input_name and value of input_value
    Tries to look for values to add human readability to and does so when possible
    Retruns a non-executable but more human readable version of the inputs in the same format
    """
    addr = AddrBook(chain)
    perm = BalPermissions(chain)
    outputs = defaultdict(list)
    for key, valuedata in contracts_inputs_values.items():
        if isinstance(valuedata, list):
            values = valuedata
        else:
            values = valuedata.strip("[ ]f").replace(" ", "").split(",")
        for value in values:
            if Web3.isAddress(value):
                outputs[key].append(
                    f"{value} ({addr.reversebook.get(web3.Web3.toChecksumAddress(value), 'N/A')}) "
                )
            elif "role" in key or "Role" in key:
                outputs[key].append(
                    f"{value} ({perm.paths_by_action_id.get(value, 'N/A')}) "
                )
            else:
                outputs[key] = valuedata
    return outputs


def merge_files(
    results_outputs_list: list[dict[str, dict[str, dict]]],
) -> dict[str, str]:
    """
    Function that merges a list of report dicts into a dict of files and report strings.


    Say we have two dictionaries in the list:
    results_outputs_list[0] = {
        "file1.json": "report1",
        "file2.json": "report2",
    }
    results_outputs_list[1] = {
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
    strings_by_file = defaultdict(str)
    for result_output in results_outputs_list:
        for file, report_data in result_output.items():
            strings_by_file[file] += report_data["report_text"]
    return strings_by_file


def extract_bip_number_from_file_name(file_name: str) -> str:
    bip = None
    # First, try to exctract BIP from file path
    if file_name is not None:
        bip_match = re.search(r"BIP-?\d+", file_name)
        bip = bip_match.group(0) if bip_match else None
    return bip or "N/A"


def extract_bip_number(bip_file: dict) -> Optional[str]:
    """
    Extracts BIP number from file path or from transactions metadata
    """
    bip = None
    # First, try to exctract BIP from file path
    if bip_file.get("file_name") is not None:
        bip_match = re.search(r"BIP-?\d+", bip_file["file_name"])
        bip = bip_match.group(0) if bip_match else None

    # If no BIP in file path, try to extract it from transactions metadata
    if not bip:
        for tx in bip_file["transactions"]:
            if tx.get("meta", {}).get("bip_number") not in [None, "N/A"]:
                bip = tx["meta"]["bip_number"]
                break
    return bip or "N/A"
