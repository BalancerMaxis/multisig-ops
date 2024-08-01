from typing import Callable
from typing import Optional

from bal_addresses import AddrBook, BalPermissions
from bal_tools import Aura
from bal_addresses import to_checksum_address, is_address
from brownie import Contract
from brownie import web3
from collections import defaultdict

from .script_utils import parse_txbuilder_list_string
from .script_utils import format_into_report
from .script_utils import get_changed_files
from .script_utils import get_pool_info
from .script_utils import merge_files
from .script_utils import extract_bip_number
from .script_utils import extract_bip_number_from_file_name
from .script_utils import get_rate_provider_review_summaries
from .script_utils import prettify_contract_inputs_values
from .script_utils import prettify_tokens_list
from .script_utils import prettify_gauge_list
from .script_utils import prettify_int_amounts, prettify_int_amount
from .script_utils import prettify_aura_pid
from .script_utils import prettify_flat_list
from .script_utils import prettify_address
from .script_utils import return_hh_brib_maps
from .script_utils import switch_chain_if_needed

from datetime import datetime

import json

GAUGE_ABI = json.load(open("abis/IChildChainGauge.json"))

ADDR_BOOK = AddrBook("mainnet")
FLATBOOK = ADDR_BOOK.flatbook
GAUGE_ADD_METHODS = ["gauge", "rootGauge"]
CMD_GAUGE_KILL = "killGauge()"
STYLE_MAINNET = "mainnet"
STYLE_SINGLE_RECIPIENT = "Single Recipient"
STYLE_CHILD_CHAIN_STREAMER = "ChildChainStreamer"
STYLE_L0 = "L0 sidechain"
CHAIN_MAINNET = "mainnet"

# Update this if needed by pulling gauge types from gauge adder:
# https://etherscan.io/address/0x5DbAd78818D4c8958EfF2d5b95b28385A22113Cd#readContract
TYPE_TO_CHAIN_MAP = {
    "Ethereum": CHAIN_MAINNET,
    "Polygon": "polygon-main",
    "Arbitrum": "arbitrum-main",
    "Optimism": "optimism-main",
    "Gnosis": "gnosis-main",
    "PolygonZkEvm": "zkevm-main",
    "Avalanche": "avax-main",
    "Base": "base-main",
    "Mode": "mode-main",
    "Fraxtal": "fraxtal-main",
    "EthereumSingleRecipientGauge": CHAIN_MAINNET,
}

SELECTORS_MAPPING = {
    "getPolygonBridge": "polygon-main",
    "getArbitrumBridge": "arbitrum-main",
    "getGnosisBridge": "gnosis-main",
    "getOptimismBridge": "optimism-main",
    "getPolygonZkEVMBridge": "zkevm-main",
    "getAvalancheBridge": "avax-main",
    "getBaseBridge": "base-main",
}

ERC20_ABI = json.load(open("abis/ERC20.json", "r"))

today = datetime.today().strftime("%Y-%m-%d")


def _extract_pool(
    chain: str, gauge: Contract, gauge_selectors: dict
) -> tuple[str, str, str, str, str, str, str, list[str], list[str]]:
    """
    Generic function used by handlers to extract pool info given chain and gauge.
    Returns pool info
    """
    # Process sidechain gauges
    if chain != CHAIN_MAINNET:
        recipient = gauge.getRecipient()
        print(f"Recipient: {recipient}")
        style = None
        network_id = ADDR_BOOK.chain_ids_by_name[
            chain.replace("-main", "").replace("avax", "avalanche")
        ]
        switch_chain_if_needed(network_id=network_id)
        try:
            sidechain_recipient = Contract(recipient)
            if "reward_receiver" in sidechain_recipient.selectors.values():
                sidechain_recipient = Contract(sidechain_recipient.reward_receiver())
                style = STYLE_CHILD_CHAIN_STREAMER
            (
                pool_name,
                pool_symbol,
                pool_id,
                pool_address,
                a_factor,
                fee,
                tokens,
                rate_providers,
            ) = get_pool_info(sidechain_recipient.lp_token())
        except ValueError as e:
            if (
                str(e)
                == "Failed to retrieve data from API: {'status': '0', 'message': 'NOTOK', 'result': 'Contract source code not verified'}"
            ):
                pool_name = "CONTRACT_UNVERIFIED"
                pool_symbol = "CONTRACT_UNVERIFIED"
                pool_id = "CONTRACT_UNVERIFIED"
                pool_address = "CONTRACT_UNVERIFIED"
                a_factor = "CONTRACT_UNVERIFIED"
                fee = "CONTRACT_UNVERIFIED"
                tokens = []
                rate_providers = []
            else:
                raise e
        style = style if style else STYLE_L0
    elif "name" not in gauge_selectors:  # Process single recipient gauges
        recipient = Contract(gauge.getRecipient())
        try:
            escrow = Contract(recipient.getVotingEscrow())
            (
                pool_name,
                pool_symbol,
                pool_id,
                pool_address,
                a_factor,
                fee,
                tokens,
                rate_providers,
            ) = get_pool_info(escrow.token())
        except AttributeError:
            # Exception Handling for single recipient gauges that are setup without using an escrow contract
            # The escrow contract is normally the thing that holds all the data about the pool.
            print(
                f"WARNING!!  Single recipient gauge found with no escrow/clear attement to a pool at {gauge.address} points to {gauge.getRecipient()}"
            )
            pool_name = "UNKNOWN - No escrow"
            pool_symbol = "N/A"
            pool_id = "N/A - No Escrow"
            pool_address = "N/A"
            a_factor = "N/A"
            fee = "N/A"
            tokens = ["UNKNOWN"]
            rate_providers = ["UNKNOWN"]
        style = STYLE_SINGLE_RECIPIENT
    else:  # Process mainnet gauges
        (
            pool_name,
            pool_symbol,
            pool_id,
            pool_address,
            a_factor,
            fee,
            tokens,
            rate_providers,
        ) = get_pool_info(gauge.lp_token())
        style = STYLE_MAINNET
    tokens = prettify_tokens_list(tokens)
    return (
        pool_name,
        pool_symbol,
        pool_id,
        pool_address,
        a_factor,
        fee,
        style,
        tokens,
        rate_providers,
    )


def _parse_aura_direct_incentive(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse injector changes

    Look up injector addresses and parse amounts.

    :param transaction: transaction to parse
    :return: dict with parsed data
    """
    chain_id = kwargs["chain_id"]
    chain_name = AddrBook.chain_names_by_id.get(int(chain_id))
    chainbook = AddrBook(chain_name)
    aura = Aura(chain_name)
    if not transaction.get("contractInputsValues") or not transaction.get(
        "contractMethod"
    ):
        return
    if not transaction["contractMethod"].get("name") == "fundPool":
        return
    to_address = to_checksum_address(transaction["to"])
    switch_chain_if_needed(chain_id)
    injector = Contract(to_address)
    tokenAddress = to_checksum_address(transaction["contractInputsValues"]["_token"])
    with open("abis/ERC20.json", "r") as f:
        token = Contract.from_abi("Token", tokenAddress, json.load(f))
    decimals = token.decimals()
    symbol = token.symbol()
    aura_pid = transaction["contractInputsValues"]["_pid"]
    amount = transaction["contractInputsValues"]["_amount"]
    periods = transaction["contractInputsValues"]["_periods"]
    pretty_pid = prettify_aura_pid(aura_pid, aura)
    pretty_amount = prettify_int_amount(amount, decimals)
    return {
        "function": "fundPool",
        "chain": chainbook.chain,
        "injector": f"{to_address}({chainbook.reversebook.get(to_address, 'Not Found')})",
        "symbol": symbol,
        "gauge_info": pretty_pid,
        "amount_per_period": pretty_amount,
        "periods": periods,
        "tx_index": kwargs.get("tx_index", "N/A"),
    }


def _parse_set_recipient_list(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse injector changes

    Look up injector addresses and parse amounts.

    :param transaction: transaction to parse
    :return: dict with parsed data
    """
    chain_id = kwargs["chain_id"]
    chain_name = AddrBook.chain_names_by_id.get(int(chain_id))
    chainbook = AddrBook(chain_name)
    if not transaction.get("contractInputsValues") or not transaction.get(
        "contractMethod"
    ):
        return
    if not transaction["contractMethod"].get("name") == "setRecipientList":
        return
    to_address = to_checksum_address(transaction["to"])
    switch_chain_if_needed(chain_id)
    injector = Contract(to_address)
    tokenAddress = injector.getInjectTokenAddress()
    with open("abis/ERC20.json", "r") as f:
        token = Contract.from_abi("Token", tokenAddress, json.load(f))
    decimals = token.decimals()
    symbol = token.symbol()
    gauge_addresses = parse_txbuilder_list_string(
        transaction["contractInputsValues"]["gaugeAddresses"]
    )
    amounts_per_period = parse_txbuilder_list_string(
        transaction["contractInputsValues"]["amountsPerPeriod"]
    )
    max_periods = parse_txbuilder_list_string(
        transaction["contractInputsValues"]["maxPeriods"]
    )
    assert len(gauge_addresses) == len(amounts_per_period) and len(
        gauge_addresses
    ) == len(
        max_periods
    ), f"List lentgh mismatch gauges:{len(gauge_addresses)}, amounts:{len(amounts_per_period)}, max_periods:{len(max_periods)}"
    pretty_gauges = prettify_gauge_list(gauge_addresses, chainbook)
    pretty_amounts = prettify_int_amounts(amounts_per_period, decimals)
    total_amount_first_period = sum([int(x) for x in amounts_per_period])
    return {
        "function": "setRecipientList",
        "chain": chainbook.chain,
        "injector": f"{to_address}({chainbook.reversebook.get(to_address, 'Not Found')})",
        "symbol": symbol,
        "gaugeList": json.dumps(pretty_gauges, indent=1),
        "amounts_per_period": json.dumps(pretty_amounts, indent=1),
        "periods": json.dumps(max_periods, indent=1),
        "total_amount_first_period": f"raw: {total_amount_first_period}/1e{decimals} = {total_amount_first_period / 10 ** decimals}",
        "tx_index": kwargs.get("tx_index", "N/A"),
    }


def _parse_hh_brib(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse Hidden Hand Bribe transactions

    Look up the proposals and return a human readable pool + amount.

    :param transaction: transaction to parse
    :return: dict with parsed data
    """
    chain_id = kwargs["chain_id"]
    chain_name = AddrBook.chain_names_by_id.get(int(chain_id))
    chainbook = AddrBook(chain_name)
    switch_chain_if_needed(chain_id)
    if not transaction.get("contractInputsValues") or not transaction.get(
        "contractMethod"
    ):
        return
    if not transaction["contractMethod"].get("name") == "depositBribe":
        return
    ## Grab Proposal data and briber addresses
    prop_map = return_hh_brib_maps()
    aura_briber = chainbook.extras.hidden_hand2.get("aura_briber")
    bal_briber = chainbook.extras.hidden_hand2.get("balancer_briber")
    ##  Parse TX
    ### Determine market
    to_address = to_checksum_address(transaction["to"])
    print(
        f"Selecting markets on {chain_name} based on: aura briber: {aura_briber}, bal_briber: {bal_briber}"
    )
    if to_address == aura_briber:
        market = "aura"
    elif to_address == bal_briber:
        market = "balancer"
    else:
        print(
            f"Couldn't determine bribe market for {json.dumps(transaction, indent=2)}"
        )
        return
    ### Grab info
    token_address = transaction["contractInputsValues"].get("_token")
    raw_amount = int(transaction["contractInputsValues"]["_amount"])
    proposal_hash = transaction["contractInputsValues"]["_proposal"]
    periods = transaction["contractInputsValues"].get("_periods", "N/A")

    ## Try to connect to the token interface to get more details
    try:
        token = Contract.from_abi("Token", token_address, ERC20_ABI)
        token_symbol = token.symbol()
        whole_amount = raw_amount / 10 ** token.decimals()

    except Exception as e:
        print(f"Warning.  Can't interface with token contract {token_address}: {e}")
        token_symbol = "N/A"
        whole_amount = "N/A"

    ### Lookup Proposal and return report
    prop_data = prop_map[market].get(proposal_hash)
    if not isinstance(prop_data, dict):
        return {
            "function": "depositBribe",
            "chain": chainbook.chain,
            "error": f"Can not find proposal {proposal_hash} on the {market} incentive market.",
            "bip": kwargs.get("bip_number", "N/A"),
            "tx_index": kwargs.get("tx_index", "N/A"),
        }

    return {
        "function": "depositBribe",
        "chain": chainbook.chain,
        "title_and_poolId": f"{prop_data.get('title', 'Not Found')} \n{prop_data.get('poolId', 'Not Found')}",
        "incentive_paid": f"{token_symbol}({token_address}) \n {whole_amount}({raw_amount})",
        "market_and_prophash": f"{market} \n{proposal_hash}",
        "periods": periods,
        "tx_index": kwargs.get("tx_index", "N/A"),
    }


def _parse_added_transaction(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse a gauge adder transaction and return a dict with parsed data.

    First, it tries to extract gauge address from the transaction data.
    If it fails, it tries to extract gauge address from the transaction input.

    Then, it extracts gauge data from mainnet or jump to sidechains if needed.

    :param transaction: transaction to parse
    :return: dict with parsed data
    """
    if not transaction.get("contractInputsValues") or not transaction.get(
        "contractMethod"
    ):
        return
    # Parse only gauge add transactions
    if not any(
        method in transaction["contractInputsValues"] for method in GAUGE_ADD_METHODS
    ):
        return
    # Find command and gauge address
    command = transaction["contractMethod"]["name"]
    gauge_type = transaction["contractInputsValues"].get("gaugeType")
    if not gauge_type:
        print("No gauge type found! Cannot process transaction")
        return
    if (
        transaction["to"]
        != ADDR_BOOK.search_unique("20230519-gauge-adder-v4/GaugeAdder").address
    ):
        return
    # Reset connection to mainnet
    switch_chain_if_needed(network_id=1)

    chain = TYPE_TO_CHAIN_MAP.get(gauge_type)
    gauge_address = None
    for method in GAUGE_ADD_METHODS:
        gauge_address = transaction["contractInputsValues"].get(method)
        if gauge_address:
            break
    if not gauge_address:
        print("! Gauge address not found in transaction data")
        return
    # Finally, extract gauge data from mainnet or jump to sidechains if needed
    gauge = Contract(gauge_address)
    gauge_selectors = gauge.selectors.values()
    gauge_cap = (
        f"{gauge.getRelativeWeightCap() / 10 ** 16}%"
        if "getRelativeWeightCap" in gauge_selectors
        else "N/A"
    )
    # Process sidechain gauges
    print(f"root gauge: {gauge_address}")
    (
        pool_name,
        pool_symbol,
        pool_id,
        pool_address,
        a_factor,
        fee,
        style,
        tokens,
        rate_providers,
    ) = _extract_pool(chain, gauge, gauge_selectors)
    addr = AddrBook("mainnet")
    to = transaction["to"]
    to_name = addr.reversebook.get(to, "!!NOT-FOUND")
    if to_name == "20230519-gauge-adder-v4/GaugeAdder":
        to_string = "GaugeAdderV4"
    elif isinstance(to_name, str):
        to_string = f"!!f{to_name}??"

    return {
        "function": f"{to_string}/{command}",
        "chain": chain.replace("-main", "") if chain else "mainnet",
        "pool_id_and_address": f"{pool_id} \npool_address: {pool_address}",
        "symbol_and_info": f"{pool_symbol} \nfee: {fee}\na-factor: {a_factor}",
        "gauge_address_and_info": f"{gauge_address}\nStyle: {style}\ncap: {gauge_cap}",
        "tokens": "\n".join(tokens),
        "rate_providers": "\n".join(rate_providers),
        "review_summary": "\n".join(
            get_rate_provider_review_summaries(rate_providers, chain)
        ),
        "bip": kwargs.get("bip_number", "N/A"),
        "tx_index": kwargs.get("tx_index", "N/A"),
    }


def _parse_removed_transaction(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse a gauge remover transaction and return a dict with parsed data.
    """
    if not transaction.get("contractInputsValues") or not transaction.get(
        "contractMethod"
    ):
        return
    input_values = transaction.get("contractInputsValues")
    if not input_values or not isinstance(input_values, dict):
        return
    encoded_data = input_values.get("data")
    if not encoded_data:
        return

    switch_chain_if_needed(network_id=1)
    try:
        (command, inputs) = Contract(
            to_checksum_address(transaction["contractInputsValues"]["target"])
        ).decode_input(transaction["contractInputsValues"]["data"])
    except:
        ## Doesn't look like a gauge add, maybe contract isn't on mainnet
        return

    if len(inputs) == 0 and command == CMD_GAUGE_KILL:
        gauge_address = transaction["contractInputsValues"]["target"]
    else:
        print("Parse KillGauge: Not a gauge kill transaction")
        return
    gauge = Contract(gauge_address)
    gauge_selectors = gauge.selectors.values()
    gauge_cap = (
        f"{gauge.getRelativeWeightCap() / 10 ** 16}%"
        if "getRelativeWeightCap" in gauge_selectors
        else "N/A"
    )
    if gauge._name == "AvalancheRootGauge":
        chain = "avax-main"
    elif gauge._name == "PolygonZkEVMRootGauge":
        chain = "zkevm-main"
    elif gauge._name == "PolygonRootGauge":
        chain = "polygon-main"
    elif gauge._name == "ArbitrumRootGauge":
        chain = "arbitrum-main"
    elif gauge._name == "OptimismRootGauge":
        chain = "optimism-main"
    elif gauge._name == "GnosisRootGauge":
        chain = "gnosis-main"
    elif gauge._name == "BaseRootGauge":
        chain = "base-main"
    else:
        # Find intersection between gauge selectors and SELECTORS_MAPPING
        chain = CHAIN_MAINNET
        for selector in gauge_selectors:
            if selector in SELECTORS_MAPPING.keys():
                chain = SELECTORS_MAPPING[selector]
                break

    (
        pool_name,
        pool_symbol,
        pool_id,
        pool_address,
        a_factor,
        fee,
        style,
        tokens,
        rate_providers,
    ) = _extract_pool(chain, gauge, gauge_selectors)

    addr = AddrBook("mainnet")
    to = transaction["to"]
    to_name = addr.reversebook.get(to, "!!NOT-FOUND")
    if to_name == "20221124-authorizer-adaptor-entrypoint/AuthorizerAdaptorEntrypoint":
        to_string = "AAEntrypoint"
    elif isinstance(to_name, str):
        to_string = f"!!f{to_name}??"

    return {
        "function": f"{to_string}/{command}",
        "chain": chain.replace("-main", "") if chain else "mainnet",
        "pool_id": pool_id,
        "symbol": pool_symbol,
        "a": a_factor,
        "gauge_address": gauge_address,
        "fee": f"{fee}%",
        "cap": gauge_cap,
        "style": style,
        "bip": kwargs.get("bip_number", "N/A"),
        "tx_index": kwargs.get("tx_index", "N/A"),
        "tokens": tokens,
    }


def _parse_permissions(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse Permissions changes made to the authorizer
    """
    if not transaction.get("contractInputsValues") or not transaction.get(
        "contractMethod"
    ):
        return
    function = transaction["contractMethod"].get("name")
    ## Parse only role changes
    if "Role" not in function:
        return
    chain_id = kwargs["chain_id"]
    chain_name = AddrBook.chain_names_by_id.get(int(chain_id))
    if not chain_name:
        print("Chain name not found! Can not parse transaction.")
        return
    perms = BalPermissions(chain_name)
    addr = AddrBook(chain_name)
    action_ids = transaction["contractInputsValues"].get("roles")
    # Change from a txbuilder json format list of addresses to a python one
    if not action_ids:
        action_ids = [transaction["contractInputsValues"].get("role")]
    elif isinstance(action_ids, str):
        action_ids = action_ids.strip("[ ]")
        action_ids = action_ids.replace(" ", "")
        action_ids = action_ids.split(",")
    if not isinstance(action_ids, list):
        print(
            f"Function {function} came up with {action_ids} which is not a valid list."
        )
        return
    to = transaction["to"]
    to_name = addr.reversebook.get(to, "!!NOT-FOUND")
    if to_name == "20210418-authorizer/Authorizer":
        to_string = "Authorizer"
    elif isinstance(to_name, str):
        to_string = f"!!{to_name}??"
    caller_address = transaction["contractInputsValues"].get("account")
    caller_name = addr.reversebook.get(caller_address, "!!NOT FOUND!!")
    fx_paths = []
    for action_id in action_ids:
        paths = perms.paths_by_action_id[action_id]
        fx_paths = [*fx_paths, *paths]
    return {
        "function": f"{to_string}/{function}",
        "chain": chain_name,
        "caller_name": caller_name,
        "caller_address": caller_address,
        "fx_paths": "\n".join([i for i in fx_paths]),
        "action_ids": "\n".join([i for i in action_ids]),
        "bip": kwargs.get("bip_number", "N/A"),
        "tx_index": kwargs.get("tx_index", "N/A"),
    }


def _parse_AuthorizerAdapterEntrypoint(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse calls made throught the AuthorizerAdapterEntrypoint
    """
    if not transaction.get("contractInputsValues") or not transaction.get(
        "contractMethod"
    ):
        return
    # Parse only gauge add transactions
    if transaction["contractMethod"]["name"] != "performAction":
        return
    chain_id = kwargs["chain_id"]
    chain_alias = "{}-main"
    chain_name = "main"
    # Get chain name using address book and chain id
    for c_name, c_id in AddrBook.chain_ids_by_name.items():
        if int(chain_id) == int(c_id):
            chain_name = (
                chain_alias.format(c_name) if c_name != "mainnet" else "mainnet"
            )
            chainbook = AddrBook(c_name)
            break
    switch_chain_if_needed(chain_id)
    entrypoint = Contract(transaction["to"])
    # try:
    target_address = transaction["contractInputsValues"].get("target")
    print(target_address)
    try:
        target_interface = Contract.from_explorer(target_address)
    except Exception as e:
        try:
            print(
                f"WARNING: Attempting to use Gauge Interface for {target_address} instead of explorer due to failure:{e}"
            )
            target_interface = Contract.from_abi("gauge", target_address, GAUGE_ABI)
            # check and make sure this looks like a gauge
            target_interface.lp_token()
        except Exception as e:
            print(f"Can't find target interface for {target_address}: {e}")
            return
    try:
        data = transaction["contractInputsValues"].get("data")
        (selector, inputs) = target_interface.decode_input(data)
    except Exception as e:
        print(f"Error processing performAction call: {e}")
        return
    try:
        inputs = prettify_flat_list(inputs, chain_name)
    except Exception as e:
        print(
            f"INFO: Was unable to prettify inputs during performAction decoding, perhaps the input data is too complex: {e}"
        )
    return {
        "function": "performAction",
        "chain": chain_name,
        "entrypoint": prettify_address(entrypoint.address, chainbook),
        "target": prettify_address(target_address, chainbook),
        "selector": selector,
        "parsed_inputs": "\n".join(inputs),
        "bip": kwargs.get("bip_number", "N/A"),
        "tx_index": kwargs.get("tx_index", "N/A"),
    }


def _parse_transfer(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse an ERC-20 transfer transaction and return a dict with parsed data
    """
    if not transaction.get("contractInputsValues") or not transaction.get(
        "contractMethod"
    ):
        return
    # Parse only gauge add transactions
    if transaction["contractMethod"]["name"] != "transfer":
        return

    chain_id = kwargs["chain_id"]
    chain_alias = "{}-main"
    chain_name = "main"
    # Get chain name using address book and chain id
    for c_name, c_id in AddrBook.chain_ids_by_name.items():
        if int(chain_id) == int(c_id):
            chain_name = (
                chain_alias.format(c_name) if c_name != "mainnet" else "mainnet"
            )
            addresses = AddrBook(c_name)
            break
    if not chain_name:
        print("Chain name not found! Cannot transfer transaction")
        return
    switch_chain_if_needed(chain_id)
    # Get input values
    try:
        token = Contract(transaction["to"])
    except Exception as e:
        print(f"Failed to get token contract: {e}")
        return
    recipient_address = (
        transaction["contractInputsValues"].get("to")
        or transaction["contractInputsValues"].get("dst")
        or transaction["contractInputsValues"].get("recipient")
        or transaction["contractInputsValues"].get("_to")
    )
    if is_address(recipient_address):
        recipient_address = to_checksum_address(recipient_address)
    else:
        print("ERROR: can't find recipient address")
        recipient_address = None
    raw_amount = (
        transaction["contractInputsValues"].get("amount")
        or transaction["contractInputsValues"].get("value")
        or transaction["contractInputsValues"].get("wad")
        or transaction["contractInputsValues"].get("_value")
    )
    amount = int(raw_amount) / 10 ** token.decimals() if raw_amount else "N/A"
    symbol = token.symbol()
    recipient_name = addresses.reversebook.get(recipient_address, "N/A")
    return {
        "function": "transfer",
        "chain": chain_name.replace("-main", "") if chain_name else "mainnet",
        "token_symbol": f"{symbol}:{token.address}",
        "recipient": f"{recipient_name}:{recipient_address}",
        "amount": f"{amount} (RAW: {raw_amount})",
        "bip": kwargs.get("bip_number", "N/A"),
        "tx_index": kwargs.get("tx_index", "N/A"),
    }


def parse_no_reports_report(
    all_reports: list[dict[str, dict]], files: list[dict]
) -> dict[str, dict]:
    """
    Accepts a list of report outputs returned from the handler, and the files list.
    Returns a report with details about any transactions, which have not been otherwise reported on in the same format
    as the input reports in the list.
    """
    covered_indexs_by_file = {}
    reports = defaultdict(dict)
    uncovered_indexes_by_file = defaultdict(set)
    tx_list_len_by_file = defaultdict(int)
    filedata_by_file = defaultdict(dict)
    # Generate a dict of sets of all files checked and a dict of all filedatas
    for file in files:
        tx_list_len_by_file[file["file_name"]] = len(file["transactions"])
        covered_indexs_by_file[file["file_name"]] = set()
        filedata_by_file[file["file_name"]] = file
    # Figure out covered indexes per file based on provided reports
    for report_info in all_reports:
        for filename, info in report_info.items():
            for output in info["report_data"]["outputs"]:
                covered_indexs_by_file[filename].add(output.get("tx_index"))
    # Figure out uncovered indexes in the dict and report on them
    for filename, covered_indexes in covered_indexs_by_file.items():
        all_indexes = range(tx_list_len_by_file[filename])
        uncovered_indexs = set(all_indexes).symmetric_difference(covered_indexes)
        # If there are no covered indexes this returns an empty set, but we know there is 1 uncovered tx at index 0
        if len(covered_indexes) == 0:
            uncovered_indexs.add(0)
        print(
            f"{filename}: covered: {covered_indexes}, uc:{uncovered_indexs}, all: {all_indexes}"
        )
        if len(uncovered_indexs) == 0:
            print(f"BINGO!  100% coverage for {filename}")
            continue
        uncovered_indexes_by_file[filename] = uncovered_indexs
        multisig = filedata_by_file[filename]["meta"]["createdFromSafeAddress"]
        chain_id = filedata_by_file[filename]["chainId"]
        chain_name = AddrBook.chain_names_by_id.get(int(chain_id), "Chain_not_found")
        addr = AddrBook(chain_name)
        no_reports = []
        for i in uncovered_indexs:
            transaction = filedata_by_file[filename]["transactions"][i]
            #  Now we can do the reporting magic on each uncovered transaction
            to = transaction["to"]
            bip_number = transaction.get("meta", {}).get(
                "bip_number"
            ) or extract_bip_number_from_file_name(filename)
            civ = transaction.get("contractInputsValues")
            if isinstance(civ, dict):
                civ_parsed = prettify_contract_inputs_values(
                    chain_name, transaction["contractInputsValues"]
                )
            elif transaction.get("data"):
                civ_parsed = transaction["data"]
            else:
                civ_parsed = "N/A"
            contractMethod = transaction.get("contractMethod", {})
            value = transaction.get("value")
            if value:
                # value is always gas token, which in our cases is always 1e18, don't need math for 0
                value = int(value)
                if value == 0:
                    valuestring = str(value)
                else:
                    valuestring = f"{value}/1e18 = {int(value) / 1e18}"
            else:
                valuestring = "N/A"
            no_reports.append(
                {
                    "fx_name": (
                        contractMethod.get("name", "!!N/A!!")
                        if contractMethod
                        else "!!N/A!!"
                    ),
                    "to": f"{to} ({addr.reversebook.get(to, 'Not Found')})",
                    "chain": chain_name,
                    "value": valuestring,
                    "inputs": json.dumps(civ_parsed, indent=2),
                    "bip_number": bip_number,
                    "tx_index": transaction.get("tx_index", "N/A"),
                }
            )

        reports[filename] = {
            "report_text": format_into_report(
                filedata_by_file[filename],
                no_reports,
                multisig,
                int(chain_id),
            ),
            "report_data": {"file": {"file_name": filename}, "outputs": no_reports},
        }
    return reports


def handler(files: list[dict], handler_func: Callable) -> dict[str, dict]:
    """
    Process a list of files and return a dict with parsed data.
    """
    reports = {}
    print(f"Processing {len(files)} files... with {handler_func.__name__}")
    for file in files:
        outputs = []
        tx_list = file["transactions"]
        i = 0
        for transaction in tx_list:
            data = handler_func(
                transaction,
                chain_id=file["chainId"],
                # Try to extract bip number from transaction meta first. If it's missing,
                # It means merge jsons hasn't been run yet, so we extract it from the file name
                bip_number=transaction.get("meta", {}).get("bip_number")
                or extract_bip_number(file),
                tx_index=i,
            )
            if data:
                outputs.append(data)
            i += 1
        if outputs:
            reports[file["file_name"]] = {
                "report_text": format_into_report(
                    file,
                    outputs,
                    file["meta"]["createdFromSafeAddress"],
                    int(file["chainId"]),
                ),
                "report_data": {"file": file, "outputs": outputs},
            }
    return reports


def main() -> None:
    files = get_changed_files()
    print(f"Found {len(files)} files with added/removed gauges")
    # TODO: Add here more handlers for other types of transactions
    all_reports = []
    all_reports.append(handler(files, _parse_added_transaction))
    all_reports.append(handler(files, _parse_removed_transaction))
    all_reports.append(handler(files, _parse_transfer))
    all_reports.append(handler(files, _parse_permissions))
    all_reports.append(handler(files, _parse_hh_brib))
    all_reports.append(handler(files, _parse_aura_direct_incentive))
    all_reports.append(handler(files, _parse_AuthorizerAdapterEntrypoint))
    all_reports.append(handler(files, _parse_set_recipient_list))

    ## Catch All should run after all other handlers.
    no_reports_report = parse_no_reports_report(all_reports, files)
    all_reports.append(no_reports_report)
    merged_files = merge_files(all_reports)
    # Save report to report.txt file
    if merged_files:
        with open("payload_reports.txt", "w") as f:
            for report in merged_files.values():
                f.write(report)
    for filename, report in merged_files.items():
        # Replace .json with .report.txt
        filename = filename.replace(".json", ".report.txt")
        with open(f"../../{filename}", "w") as f:
            f.write(report)


if __name__ == "__main__":
    main()
