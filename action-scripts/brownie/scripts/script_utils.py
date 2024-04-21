import json
import os
import re
from decimal import Decimal
from json import JSONDecodeError
from typing import Optional

from tabulate import tabulate
from collections import defaultdict
from bal_addresses import AddrBook, BalPermissions
import requests
from brownie import Contract, chain, network, web3
from eth_abi import encode_abi
from gnosis.eth import EthereumClient
from gnosis.eth.constants import NULL_ADDRESS
from gnosis.safe import SafeOperation
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx


ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

NA = "N/A"
NOT_FOUND = "Not Found"
POOL_ID_CUSTOM_FALLBACK = "Custom"
BIPS_PRECISION = 1e16


def return_hh_brib_maps() -> dict:
    """
    Grabs and reformats hidden hand API data into a dict that has data for each proposal formatted like prop.market.prop_data_dict
    """
    hh_bal_props = requests.get("https://api.hiddenhand.finance/proposal/balancer")
    hh_bal_props.raise_for_status()
    hh_aura_props = requests.get("https://api.hiddenhand.finance/proposal/aura")
    hh_aura_props.raise_for_status()
    results = {"aura": {}, "balancer": {}}
    for prop in hh_bal_props.json()["data"]:
        results["balancer"][prop["proposalHash"]] = prop
    for prop in hh_aura_props.json()["data"]:
        results["aura"][prop["proposalHash"]] = prop
    return results


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
        if "BIPs/" or "MaxiOps/" in filename and filename.endswith(".json"):
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
    if len(rate_providers) == 0:
        try:
            rehype_pool = Contract.from_explorer(pool_address)
            rate_providers.append(rehype_pool.rateProvider0())
            rate_providers.append(rehype_pool.rateProvider1())
        except Exception:
            pass
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


def switch_chain_if_needed(network_id: int) -> None:
    network_id = int(network_id)
    if web3.chain_id != network_id:
        network.disconnect()
        chain_name = AddrBook.chain_names_by_id[int(network_id)]
        chain_name = "avax" if chain_name == "avalanche" else chain_name
        chain_name = f"{chain_name}-main" if chain_name != "mainnet" else "mainnet"
        print("reconnecting to", chain_name)
        network.connect(chain_name)
        assert web3.chain_id == network_id, (web3.chain_id, network_id)
        assert network.is_connected()


def run_tenderly_sim(network_id: str, safe_addr: str, transactions: list[dict]):
    """
    generates a tenderly simulation
    returns the url and if it was successful or not
    """
    # build urls
    user = os.getenv("TENDERLY_ACCOUNT_NAME")
    project = os.getenv("TENDERLY_PROJECT_NAME")
    if not user or not project:
        return "N/A", "NOT RUN/NO CREDENTIALS"
    sim_base_url = f"https://dashboard.tenderly.co/{user}/{project}/simulator/"
    api_base_url = f"https://api.tenderly.co/api/v1/account/{user}/project/{project}"

    # reset connection to network on which the safe is deployed
    switch_chain_if_needed(network_id)

    # build individual tx data
    for tx in transactions:
        if tx["contractMethod"]:
            tx["contractMethod"]["type"] = "function"
            contract = web3.eth.contract(
                address=web3.toChecksumAddress(tx["to"]), abi=[tx["contractMethod"]]
            )
            if len(tx["contractMethod"]["inputs"]) > 0:
                for input in tx["contractMethod"]["inputs"]:
                    if "bool" in input["type"]:
                        if "[]" in input["type"]:
                            if type(tx["contractInputsValues"][input["name"]]) != list:
                                tx["contractInputsValues"][input["name"]] = [
                                    (True if x == "true" else False)
                                    for x in tx["contractInputsValues"][input["name"]]
                                    .strip("[]")
                                    .split(",")
                                ]
                        else:
                            tx["contractInputsValues"][input["name"]] = (
                                True
                                if tx["contractInputsValues"][input["name"]] == "true"
                                else False
                            )
                    if re.search(r"int[0-9]+", input["type"]):
                        if "[]" in input["type"]:
                            if type(tx["contractInputsValues"][input["name"]]) != list:
                                tx["contractInputsValues"][input["name"]] = [
                                    int(x)
                                    for x in tx["contractInputsValues"][input["name"]]
                                    .strip("[]")
                                    .split(",")
                                ]
                        else:
                            tx["contractInputsValues"][input["name"]] = int(
                                tx["contractInputsValues"][input["name"]]
                            )
                    if "address" in input["type"]:
                        if "[]" in input["type"]:
                            if type(tx["contractInputsValues"][input["name"]]) != list:
                                tx["contractInputsValues"][input["name"]] = [
                                    web3.toChecksumAddress(x)
                                    for x in tx["contractInputsValues"][input["name"]]
                                    .strip("[]")
                                    .split(",")
                                ]
                        else:
                            tx["contractInputsValues"][input["name"]] = (
                                web3.toChecksumAddress(
                                    tx["contractInputsValues"][input["name"]]
                                )
                            )
                tx["data"] = contract.encodeABI(
                    fn_name=tx["contractMethod"]["name"],
                    args=list(tx["contractInputsValues"].values()),
                )
            else:
                tx["data"] = contract.encodeABI(
                    fn_name=tx["contractMethod"]["name"], args=[]
                )

    # build multicall data
    multisend_call_only = MultiSend.MULTISEND_CALL_ONLY_ADDRESSES[0]
    txs = [
        MultiSendTx(MultiSendOperation.CALL, tx["to"], int(tx["value"]), tx["data"])
        for tx in transactions
    ]
    data = MultiSend(EthereumClient(web3.provider.endpoint_uri)).build_tx_data(txs)
    safe = web3.eth.contract(
        address=safe_addr, abi=json.load(open("abis/IGnosisSafe.json", "r"))
    )
    owners = list(safe.functions.getOwners().call())

    # build execTransaction data
    # execTransaction(address,uint256,bytes,uint8,uint256,uint256,uint256,address,address,bytes)
    exec_tx = {
        "to": multisend_call_only,
        "value": 0,
        "data": data,
        "operation": SafeOperation.DELEGATE_CALL.value,
        "safeTxGas": 0,
        "baseGas": 0,
        "gasPrice": 0,
        "gasToken": NULL_ADDRESS,
        "refundReceiver": NULL_ADDRESS,
        "signatures": b"".join(
            [
                encode_abi(["address", "uint"], [str(owner), 0]) + b"\x01"
                for owner in owners
            ]
        ),
    }
    input = safe.encodeABI(fn_name="execTransaction", args=list(exec_tx.values()))

    # build tenderly data
    data = {
        "network_id": network_id,
        "from": owners[0],
        "to": safe_addr,
        "input": input,
        "save": True,
        "save_if_fails": True,
        "simulation_type": "quick",
        "state_objects": {
            safe_addr: {
                "storage": {
                    "0x0000000000000000000000000000000000000000000000000000000000000004": "0x0000000000000000000000000000000000000000000000000000000000000001"
                }
            }
        },
    }

    # post to tenderly api
    r = requests.post(
        url=f"{api_base_url}/simulate",
        json=data,
        headers={
            "X-Access-Key": os.getenv("TENDERLY_ACCESS_KEY"),
            "Content-Type": "application/json",
        },
    )
    try:
        r.raise_for_status()
    except:
        print(r.json())

    result = r.json()

    # make the simulation public
    r = requests.post(
        url=f"{api_base_url}/simulations/{result['simulation']['id']}/share",
        headers={
            "X-Access-Key": os.getenv("TENDERLY_ACCESS_KEY"),
            "Content-Type": "application/json",
        },
    )
    try:
        r.raise_for_status()
    except:
        print(r.json())

    url = f"https://www.tdly.co/shared/simulation/{result['simulation']['id']}"
    success = result["simulation"]["status"]
    return url, success


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
    msig_label = book.reversebook.get(web3.toChecksumAddress(msig_addr), "!NOT FOUND")
    file_name = file["file_name"]
    print(f"Writing report for {file_name}...")
    file_report = f"FILENAME: `{file_name}`\n"
    file_report += f"MULTISIG: `{msig_label} ({AddrBook.chain_names_by_id[chain_id]}:{msig_addr})`\n"
    file_report += f"COMMIT: `{os.getenv('COMMIT_SHA', 'N/A')}`\n"
    # Format chains and remove "-main" from suffix of chain name
    chains = set(
        map(
            lambda chain: chain.replace("-main", ""),
            [transaction["chain"] for transaction in transactions],
        )
    )
    file_report += f"CHAIN(S): `{', '.join(chains)}`\n"
    tenderly_url, tenderly_success = run_tenderly_sim(
        file["chainId"], file["meta"]["createdFromSafeAddress"], file["transactions"]
    )
    if tenderly_success:
        file_report += f"TENDERLY: [SUCCESS]({tenderly_url})\n"
    else:
        file_report += f"TENDERLY: [FAILURE]({tenderly_url})\n"
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


def prettify_int_amounts(amounts: list, decimals=None) -> list[str]:
    pretty_amounts = []
    for amount in amounts:
        try:
            amount = int(amount)
        except:
            # Can't make this an int, leave it alone
            print(f"Can't make {amount} into an int to prettify")
            pretty_amounts.append(amount)
            continue
        if isinstance(decimals, int):
            # We know decimals so use them
            pretty_amounts.append(f"{amount}/1e{decimals} = {amount/10**decimals}")
        else:
            # We don't know decimals so provide 18 and 6
            pretty_amounts.append(
                f"raw:{amount}, 18 decimals:{Decimal(amount)/Decimal(1e18)}, 6 decimals: {Decimal(amount)/Decimal(1e6)}"
            )

    return pretty_amounts


def sum_list(amounts: list) -> int:
    total = 0
    for amount in amounts:
        total += int(amount)
    return total


def prettify_contract_inputs_values(chain: str, contracts_inputs_values: dict) -> dict:
    """
    Accepts contractInputsValues dict with key of input_name and value of input_value
    Tries to look for values to add human readability to and does so when possible
    Returns a non-executable but more human readable version of the inputs in the same format
    """
    addr = AddrBook(chain)
    perm = BalPermissions(chain)
    outputs = defaultdict(list)
    for key, valuedata in contracts_inputs_values.items():
        values = parse_txbuilder_list_string(valuedata)
        for value in values:
            ## Reverse resolve addresses
            if web3.isAddress(value):
                outputs[key].append(
                    f"{value} ({addr.reversebook.get(web3.toChecksumAddress(value), 'N/A')}) "
                )
            ## Reverse resolve authorizor roles
            elif "role" in key.lower():
                outputs[key].append(
                    f"{value} ({perm.paths_by_action_id.get(value, 'N/A')}) "
                )
            elif "value" in key.lower() or "amount" in key.lower():
                # Look for things that look like values and do some decimal math
                outputs[key].append(prettify_int_amounts(values))
            else:
                outputs[key].append([value])
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


def parse_txbuilder_list_string(list_string) -> list:
    """
    Take an input from transaction builder and format it is as a list.
    If it is already a list return it
    If it is a string list from tx-builder then listify it and return that
    If it is anything else, return a single item list with whatever it is.
    """
    # Change from a txbuilder json format list of addresses to a python one
    if isinstance(list_string, str):
        list_string = list_string.strip("[ ]")
        list_string = list_string.replace(" ", "")
        list_string = list_string.split(",")
    if isinstance(list_string, list):
        return list_string
    # If we still don't have a list, create a single item list with what we do have.
    return [list_string]


def prettify_gauge_list(gauge_addresses, chainbook) -> list:
    pretty_gauges = []
    for gauge in gauge_addresses:
        gauge_name = chainbook.reversebook.get(gauge)
        if not gauge_name:
            switch_chain_if_needed(chainbook.chain_ids_by_name[chainbook.chain])
            gauge_interface = Contract(gauge)
            try:
                gauge_name = gauge_interface.name()
            except:
                gauge_name = "(N/A)"
        pretty_gauges.append(f"{gauge} ({gauge_name})")
    return pretty_gauges
