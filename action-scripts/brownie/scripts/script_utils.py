import json
import os
import re
from decimal import Decimal
from json import JSONDecodeError
from typing import Optional
from urllib.request import urlopen

from collections import defaultdict
from bal_addresses import AddrBook, BalPermissions, RateProviders
from bal_addresses import to_checksum_address, is_address
from bal_tools import Aura
import requests
from brownie import Contract, chain, network, web3
from eth_abi import encode
from gnosis.eth import EthereumClient
from gnosis.eth.constants import NULL_ADDRESS
from gnosis.safe import SafeOperation
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx
from prettytable import MARKDOWN, PrettyTable

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
        try:
            results["aura"][prop["proposalHash"]]["poolId"] = results["balancer"][
                prop["proposalHash"]
            ]["poolId"]
        except KeyError:
            pass
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
    print(f"Using {api_url} to get changed files")
    response = requests.get(api_url)
    pr_file_data = json.loads(response.text)
    changed_files = []
    for file_json in pr_file_data:
        if file_json["status"] in ["removed", "renamed"]:
            if "4269-W69" not in file_json["filename"]:
                continue
        filename = file_json["filename"]
        if ("BIPs/" or "MaxiOps/" in filename) and (filename.endswith(".json")):
            # Check if file exists first
            try:
                r = requests.get(file_json["contents_url"])
            except:
                print(f"{file_json['contents_url']} does not exist")
                continue
            # Validate that file is a valid json
            with urlopen(r.json()["download_url"]) as json_data:
                try:
                    payload = json.load(json_data)
                except JSONDecodeError:
                    print(f"{filename} is not proper json")
                    continue
                if isinstance(payload, dict) is False:
                    print(f"{filename} json is not a dict")
                    continue
                if "transactions" not in payload.keys():
                    print(f"{filename} json does not contain a list of transactions")
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
        address=book.search_unique("20210418-vault/Vault").address,
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
    table = PrettyTable(header, align="l")
    for dict_ in outputs:
        # Create a dict comprehension to include all keys and values except "chain"
        # As we don't want to display chain in the table
        dict_filtered = {k: v for k, v in dict_.items() if k != "chain"}
        table.add_row(list(dict_filtered.values()))
    table.align["review_summary"] = "c"
    table.align["bip"] = "c"
    table.align["tx_index"] = "c"
    return table.get_string()


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
        raise ValueError("TENDERLY_ACCOUNT_NAME and TENDERLY_PROJECT_NAME must be set")
    api_base_url = f"https://api.tenderly.co/api/v1/account/{user}/project/{project}"

    # reset connection to network on which the safe is deployed
    switch_chain_if_needed(network_id)

    # build individual tx data
    for tx in transactions:
        if "contractMethod" in tx and tx["contractMethod"] is not None:
            tx["contractMethod"]["type"] = "function"
            contract = web3.eth.contract(
                address=to_checksum_address(tx["to"]), abi=[tx["contractMethod"]]
            )
            if len(tx["contractMethod"]["inputs"]) > 0:
                for input in tx["contractMethod"]["inputs"]:
                    # bool
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
                    # int
                    elif re.search(r"int[0-9]+", input["type"]):
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
                    # address
                    elif "address" in input["type"]:
                        if "[]" in input["type"]:
                            if type(tx["contractInputsValues"][input["name"]]) != list:
                                tx["contractInputsValues"][input["name"]] = [
                                    to_checksum_address(x.strip())
                                    for x in tx["contractInputsValues"][input["name"]]
                                    .strip("[]")
                                    .split(",")
                                ]
                        else:
                            tx["contractInputsValues"][input["name"]] = (
                                to_checksum_address(
                                    tx["contractInputsValues"][input["name"]]
                                )
                            )
                    # tuple
                    elif "tuple" in input["type"]:
                        casted_tuple = []
                        for idx, tuple_item in enumerate(
                            tx["contractInputsValues"][input["name"]]
                            .strip("[]")
                            .split(",")
                        ):
                            try:
                                if "bool" in input["components"][idx]["type"]:
                                    casted_tuple.append(
                                        True
                                        if tuple_item.strip('"') == "true"
                                        else False
                                    )
                                elif re.search(
                                    r"int[0-9]+", input["components"][idx]["type"]
                                ):
                                    casted_tuple.append(int(tuple_item.strip('"')))
                                elif "address" in input["components"][idx]["type"]:
                                    casted_tuple.append(
                                        to_checksum_address(tuple_item.strip('"'))
                                    )
                                elif "bytes" in input["components"][idx]["type"]:
                                    casted_tuple.append(
                                        bytes(tuple_item.strip('"'), "utf-8")
                                    )
                                else:
                                    casted_tuple.append(str(tuple_item.strip('"')))
                                tx["contractInputsValues"][input["name"]] = [
                                    tuple(casted_tuple)
                                ]
                            except IndexError:
                                # payload contains nested tuples; no support yet
                                continue
                    # bytes
                    elif "bytes" in input["type"]:
                        if "[]" in input["type"]:
                            if type(tx["contractInputsValues"][input["name"]]) != list:
                                tx["contractInputsValues"][input["name"]] = [
                                    bytes(x, "utf-8").strip()
                                    for x in tx["contractInputsValues"][input["name"]]
                                    .strip("[]")
                                    .split(",")
                                ]
                        else:
                            tx["contractInputsValues"][input["name"]] = bytes(
                                tx["contractInputsValues"][input["name"]], "utf-8"
                            )
                    # catchall; cast to str
                    else:
                        if "[]" in input["type"]:
                            if type(tx["contractInputsValues"][input["name"]]) != list:
                                tx["contractInputsValues"][input["name"]] = [
                                    str(x).strip()
                                    for x in tx["contractInputsValues"][input["name"]]
                                    .strip("[]")
                                    .split(",")
                                ]
                        else:
                            tx["contractInputsValues"][input["name"]] = str(
                                tx["contractInputsValues"][input["name"]]
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
            [encode(["address", "uint"], [str(owner), 0]) + b"\x01" for owner in owners]
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

    if "simulation" not in result:
        raise ValueError(result)

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
    if result["simulation"]["status"]:
        success = "🟩 SUCCESS"
        revert_found = check_tenderly_calls_for_revert(
            result["transaction"]["transaction_info"]["call_trace"]["calls"]
        )
        if revert_found:
            success = "🟨 PARTIAL"
    else:
        success = "🟥 FAILURE"
    return url, success


def check_tenderly_calls_for_revert(calls):
    for call in calls:
        if "error_op" in call:
            if call["error_op"] == "REVERT":
                return True
        if "calls" in call:
            if isinstance(call["calls"], list):
                if check_tenderly_calls_for_revert(call["calls"]):
                    return True


def format_into_report(
    file: dict,
    transactions: list[dict],
    msig_addr: str,
    chain_id: int,
    gauge_checklist=None,
) -> str:
    """
    Formats a list of transactions into a report that can be posted as a comment on GH PR
    """
    chain_name = AddrBook.chain_names_by_id[chain_id]
    book = AddrBook(chain_name)
    msig_label = book.reversebook.get(to_checksum_address(msig_addr), "!NOT FOUND")
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
    try:
        tenderly_url, tenderly_success = run_tenderly_sim(
            file["chainId"],
            file["meta"]["createdFromSafeAddress"],
            file["transactions"],
        )
        file_report += f"TENDERLY: [`{tenderly_success}`]({tenderly_url})\n\n"
    except Exception as e:
        file_report += f"TENDERLY: `🟪 SKIPPED ({repr(e)})`\n\n"

    if gauge_checklist:
        for gauge_check in gauge_checklist:
            table = PrettyTable(align="l")
            table.set_style(MARKDOWN)
            table.field_names = [f"Gauge Validator ({gauge_check[2]})", "Result"]
            table.align["Result"] = "c"
            is_preferential = "✅" if gauge_check[0] else "❌"
            rate_providers_safety = []
            for rate_provider in gauge_check[1]:
                if rate_provider == "--":
                    continue
                rate_providers_safety.append("✅" if rate_provider == "safe" else "❌")
            table.add_row([f"`validate_preferential_gauge`", is_preferential])
            if len(rate_providers_safety) == 0:
                rate_providers_safety = ["--"]
            table.add_row(
                [f"`validate_rate_providers_safety`", " ".join(rate_providers_safety)]
            )
            file_report += table.get_string()
            file_report += "\n\n"

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


def get_rate_provider_review_summaries(
    rate_providers: list[str], chain: str
) -> list[str]:
    """
    Accepts a list of rate provider addresses and returns a list of review summaries
    """
    summaries = []
    chain = chain.removesuffix("-main")
    r = RateProviders(chain)
    if chain not in AddrBook.chain_ids_by_name.keys():
        print(f"WARNING:  Trying to look up rate-providers on unknown chain {chain}")
    for rate_provider in rate_providers:
        if rate_provider == NULL_ADDRESS:
            summaries.append("--")
            continue
        rpinfo = r.info_by_rate_provider.get(to_checksum_address(rate_provider))
        if not rpinfo:
            rpinfo = r.info_by_rate_provider.get(rate_provider.lower())
            if not rpinfo:
                print(
                    f"WARNING: looked up {to_checksum_address(rate_provider)} on chain {chain} and got {rpinfo}"
                )
                summaries.append("!!NO REVIEW!!")
            else:
                summaries.append(rpinfo["summary"])
        else:
            summaries.append(rpinfo["summary"])
    return summaries


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
        ## if empty list, return an empty list.
        if list_string == "[]":
            return []
        list_string = list_string.strip("[ ]")
        list_string = list_string.replace(" ", "")
        list_string = list_string.split(",")
        # if nothing left return an empty list
        if not list_string:
            return []
    if isinstance(list_string, list):
        return list_string
    # If we still don't have a list, create a single item list with what we do have.
    return [list_string]


def prettify_tokens_list(token_addresses: list[str]) -> list[str]:
    """
    Return a list of token addresses and names in string format.
    Uses onchain lookups with brownie, requires you are on the network of the token when run
    """
    results = []
    for token in token_addresses:
        results.append(f"{token}: {get_token_symbol(token)}")
    return results


def prettify_int_amount(amount: int, decimals=None) -> str:
    try:
        amount = int(amount)
    except:
        # Can't make this an int, leave it alone
        print(f"Can't make {amount} into an int to prettify")
        return amount
    if isinstance(decimals, int):
        # We know decimals so use them
        return f"{amount}/1e{decimals} = {amount / 10 ** decimals}"
    else:
        # We don't know decimals so provide 18 and 6
        return f"raw:{amount}, 18 decimals:{Decimal(amount) / Decimal(1e18)}, 6 decimals: {Decimal(amount) / Decimal(1e6)}"


## Prettification helpers
def prettify_int_amounts(amounts: list, decimals=None) -> list[str]:
    pretty_amounts = []
    for amount in amounts:
        pretty_amounts.append(prettify_int_amount(amount, decimals))
    return pretty_amounts


def prettify_address(address, chainbook) -> str:
    return f"{address} ({chainbook.reversebook.get(to_checksum_address(address))})"


## Prettification logic for various complex data types
def prettify_flat_list(inputs: list[str], chain: str) -> list[str]:
    """
    Accepts a list of and returns it with any address items prettified including names in string format
    Requires you are on the network of the addresses when run
    """
    chain = chain.removesuffix("-main")
    book = AddrBook(chain)
    results = []
    for input in inputs:
        if is_address(input):
            results.append(
                f"{input}: {book.reversebook.get(to_checksum_address(input), get_token_symbol(input))}"
            )
        else:
            results.append(prettify_int_amount(input))
    return results


def prettify_contract_inputs_values(chain: str, contracts_inputs_values: dict) -> dict:
    """
    Accepts contractInputsValues dict with key of input_name and value of input_value
    Tries to look for values to add human readability to and does so when possible
    Returns a non-executable but more human readable version of the inputs in the same format
    """
    addr = AddrBook(chain)
    perm = BalPermissions(chain)
    outputs = defaultdict(list)
    ## TODO, can we use prettify flat list and the other helpers here?
    for key, valuedata in contracts_inputs_values.items():
        values = parse_txbuilder_list_string(valuedata)
        for value in values:
            ## Reverse resolve addresses
            if is_address(value):
                outputs[key].append(
                    f"{value} ({addr.reversebook.get(to_checksum_address(value), 'N/A')})"
                )
            ## Reverse resolve authorizor roles
            elif "role" in key.lower():
                outputs[key].append(
                    f"{value} ({perm.paths_by_action_id.get(value, 'N/A')})"
                )
            elif (
                "value" in key.lower()
                or "amount" in key.lower()
                or "_minouts" in key.lower()
            ):
                # Look for things that look like values and do some decimal math
                outputs[key].append(prettify_int_amount(value))
            else:
                outputs[key].append(value)
    return outputs


## TODO do we need this or can we just do a more general reverse lookup with prettify_flat_list?
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


def prettify_aura_pid(pid: int, aura: Aura) -> str:
    """
    Returns a pretty string for an aura pid
    """
    try:
        pid = int(pid)
    except Exception as e:
        print(f"Failed to convert AURA pid to int: {e}")
        return f"{pid} (!!NOT AN INT!!)"
    if not pid:
        return "N/A"
    switch_chain_if_needed(AddrBook.chain_ids_by_name[aura.chain])
    ## reverse dict aura.aura_pids_by_address such that address is key and pid is value.  Key should be a real int.
    addresses_by_pid = {int(v): k for k, v in aura.aura_pids_by_address.items()}
    gauge_address = addresses_by_pid.get(pid)
    if not gauge_address:
        return f"{pid} (!!GAUGE NOT FOUND!!)"
    gauge_interface = Contract(gauge_address)
    try:
        gauge_name = gauge_interface.name()
    except:
        gauge_name = "(N/A)"
    return f"{pid}({gauge_address})\n{gauge_name}"
