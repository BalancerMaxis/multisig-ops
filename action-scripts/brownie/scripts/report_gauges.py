from typing import Callable
from typing import Optional

from bal_addresses import AddrBook, BalPermissions, MultipleMatchesError, NoResultError
from brownie import Contract
from brownie import network
from web3 import Web3

from .script_utils import format_into_report
from .script_utils import get_changed_files
from .script_utils import get_pool_info
from .script_utils import merge_files
from .script_utils import extract_bip_number

ADDR_BOOK = AddrBook("mainnet")
FLATBOOK = ADDR_BOOK.flatbook

GAUGE_ADD_METHODS = ['gauge', 'rootGauge']
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
    "EthereumSingleRecipientGauge": CHAIN_MAINNET
}

SELECTORS_MAPPING = {
    "getTotalBridgeCost": "arbitrum-main",
    "getPolygonBridge": "polygon-main",
    "getArbitrumBridge": "arbitrum",
    "getGnosisBridge": "gnosis-main",
    "getOptimismBridge": "optimism-main",
    "getPolygonZkEVMBridge": "zkevm-main"
}


def _extract_pool(
        chain: str, gauge: Contract, gauge_selectors: dict
) -> tuple[str, str, str, str, str, str, str]:
    """
    Generic function used by handlers to extract pool info given chain and gauge.
    Returns pool info
    """
    # Process sidechain gauges
    if chain != CHAIN_MAINNET:
        recipient = gauge.getRecipient()
        network.disconnect()
        network.connect(chain)
        sidechain_recipient = Contract(recipient)
        style = None
        if "reward_receiver" in sidechain_recipient.selectors.values():
            sidechain_recipient = Contract(sidechain_recipient.reward_receiver())
            style = STYLE_CHILD_CHAIN_STREAMER
        pool_name, pool_symbol, pool_id, pool_address, a_factor, fee = get_pool_info(
            sidechain_recipient.lp_token())
        style = style if style else STYLE_L0
    elif "name" not in gauge_selectors:  # Process single recipient gauges
        recipient = Contract(gauge.getRecipient())
        escrow = Contract(recipient.getVotingEscrow())
        pool_name, pool_symbol, pool_id, pool_address, a_factor, fee = get_pool_info(escrow.token())
        style = STYLE_SINGLE_RECIPIENT
    else:  # Process mainnet gauges
        (pool_name, pool_symbol, pool_id, pool_address, a_factor, fee) = get_pool_info(
            gauge.lp_token())
        style = STYLE_MAINNET

    return pool_name, pool_symbol, pool_id, pool_address, a_factor, fee, style


def _parse_added_transaction(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse a gauge adder transaction and return a dict with parsed data.

    First, it tries to extract gauge address from the transaction data.
    If it fails, it tries to extract gauge address from the transaction input.

    Then, it extracts gauge data from mainnet or jump to sidechains if needed.

    :param transaction: transaction to parse
    :return: dict with parsed data
    """
    if network.is_connected():
        network.disconnect()
    network.connect(CHAIN_MAINNET)
    if transaction['to'] != ADDR_BOOK.search_unique("v4/GaugeAdder").address:
        return

    # Parse only gauge add transactions
    if not any(method in transaction["contractInputsValues"] for method in GAUGE_ADD_METHODS):
        return
    # Find command and gauge address
    command = transaction["contractMethod"]["name"]
    gauge_type = transaction["contractInputsValues"].get("gaugeType")
    if not gauge_type:
        print("No gauge type found! Cannot process transaction")
        return
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
        if "getRelativeWeightCap" in gauge_selectors else "N/A"
    )
    # Process sidechain gauges
    pool_name, pool_symbol, pool_id, pool_address, a_factor, fee, style = _extract_pool(
        chain, gauge, gauge_selectors
    )

    return {
        "function": command,
        "chain": chain.replace("-main", "") if chain else "mainnet",
        "pool_id": pool_id,
        "symbol": pool_symbol,
        "aFactor": a_factor,
        "gauge_address": gauge_address,
        "fee": f"{fee}%",
        "cap": gauge_cap,
        "style": style,
        "bip": kwargs.get('bip_number', 'N/A'),
        "tx_index": kwargs.get('tx_index', 'N/A'),
    }


def _parse_removed_transaction(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse a gauge remover transaction and return a dict with parsed data.
    """
    if network.is_connected():
        network.disconnect()
    network.connect(CHAIN_MAINNET)
    input_values = transaction.get("contractInputsValues")
    if not input_values or not isinstance(input_values, dict):
        return
    encoded_data = input_values.get("data")
    if not encoded_data:
        return
    (command, inputs) = Contract(
        Web3.toChecksumAddress(transaction["contractInputsValues"]["target"])
    ).decode_input(transaction["contractInputsValues"]["data"])

    if len(inputs) == 0 and command == CMD_GAUGE_KILL:
        gauge_address = transaction["contractInputsValues"]["target"]
    else:
        print("Parse KillGauge: Not a gauge kill transaction")
        return
    gauge = Contract(gauge_address)
    gauge_selectors = gauge.selectors.values()
    gauge_cap = (
        f"{gauge.getRelativeWeightCap() / 10 ** 16}%"
        if "getRelativeWeightCap" in gauge_selectors else "N/A"
    )
    gauge_selectors = gauge.selectors.values()
    # Find intersection between gauge selectors and SELECTORS_MAPPING
    chain = CHAIN_MAINNET
    for selector in gauge_selectors:
        if selector in SELECTORS_MAPPING.keys():
            chain = SELECTORS_MAPPING[selector]
            break

    pool_name, pool_symbol, pool_id, pool_address, a_factor, fee, style = _extract_pool(
        chain, gauge, gauge_selectors
    )
    return {
        "function": command,
        "chain": chain.replace("-main", "") if chain else "mainnet",
        "pool_id": pool_id,
        "symbol": pool_symbol,
        "pool_address": pool_address,
        "aFactor": a_factor,
        "gauge_address": gauge_address,
        "fee": f"{fee}%",
        "cap": gauge_cap,
        "style": style,
        "bip": kwargs.get('bip_number', 'N/A'),
        "tx_index": kwargs.get('tx_index', 'N/A'),
    }

def _parse_permissions(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse Permissions changes made to the authorizer
    """
    chain_id = kwargs["chain-id"]
    for c_name, c_id in AddrBook.chain_ids_by_name.items():
        if c_id == chain_id:
            chain_name = c_name
            break
    perms = BalPermissions(chain_name)
    addr = AddrBook(chain_name)
    function = transaction["ContractMethod"].get("name")
    ## Parse only role changes
    if "Roles" not in function:
        return
    action_ids = transaction["contractInputsValues"].get("roles")
    caller_address = transaction["contractInputsValues"].get("account")
    caller_name = addr.reverseboo.get(caller_address, "UNDEF")
    fx_paths = {}
    for action_id in action_ids:
        fx_paths.append = perms.paths_by_action_id[action_id]
    return {
        "function": function,
        "chain": chain_name,
        "caller_name": caller_name,
        "caller_address": caller_address,
        "fx_paths": fx_paths,
        "action_ids": action_ids,
        "bip": kwargs.get('bip_number', 'N/A'),
        "tx_index": kwargs.get('tx_index', 'N/A')
    }


def _parse_transfer(transaction: dict, **kwargs) -> Optional[dict]:
    """
    Parse an ERC-20 transfer transaction and return a dict with parsed data
    """

    # Parse only gauge add transactions
    if transaction["contractMethod"]["name"] != "transfer":
        return

    chain_id = kwargs["chain_id"]
    chain_alias = "{}-main"
    chain_name = "main"
    # Get chain name using address book and chain id
    for c_name, c_id in AddrBook.CHAIN_IDS_BY_NAME.items():
        if int(chain_id) == int(c_id):
            chain_name = chain_alias.format(c_name) if c_name != "mainnet" else "mainnet"
            break
    if not chain_name:
        print("Chain name not found! Cannot transfer transaction")
        return
    if network.is_connected():
        network.disconnect()
    network.connect(chain_name)
    # Get input values
    token = Contract(transaction["to"])
    recipient_address = transaction["contractInputsValues"].get("to")
    raw_amount = (
        transaction["contractInputsValues"].get("amount")
        or transaction["contractInputsValues"].get("value")
    )
    amount = int(raw_amount) / 10 ** token.decimals() if raw_amount else "N/A"
    symbol = token.symbol()
    recipient_name = ADDR_BOOK.reversebook[recipient_address] or "N/A"
    return {
        "function": "transfer",
        "chain": chain_name.replace("-main", "") if chain_name else "mainnet",
        "token_symbol": symbol,
        "recipient_name": recipient_name,
        "amount": amount,
        "token_address": token.address,
        "recipient_address": recipient_address,
        "raw_amount": raw_amount,
        "bip": kwargs.get('bip_number', 'N/A'),
        "tx_index": kwargs.get('tx_index', 'N/A'),
    }


def handler(files: list[dict], handler_func: Callable) -> dict[str, str]:
    """
    Process a list of files and return a dict with parsed data.
    """
    reports = {}
    print(f"Processing {len(files)} files... with {handler_func.__name__}")
    for file in files:
        outputs = []
        tx_list = file["transactions"]
        for transaction in tx_list:
            data = handler_func(
                transaction, chain_id=file["chainId"],
                # Try to extract bip number from transaction meta first. If it's missing,
                # It means merge jsons hasn't been run yet, so we extract it from the file name
                bip_number=transaction.get(
                    'meta', {}).get(
                    'bip_number'
                ) or extract_bip_number(file),
                tx_index=transaction.get('meta', {}).get('tx_index', "N/A")
            )
            if data:
                outputs.append(data)
        if outputs:
            reports[file['file_name']] = format_into_report(file, outputs)
    return reports


def main() -> None:
    files = get_changed_files()
    print(f"Found {len(files)} files with added/removed gauges")
    # TODO: Add here more handlers for other types of transactions
    added_gauges = handler(files, _parse_added_transaction)
    removed_gauges = handler(files, _parse_removed_transaction)
    transfer_reports = handler(files, _parse_transfer)
    permissions_reports = handler(files, _parse_permissions)

    merged_files = merge_files(added_gauges, removed_gauges, transfer_reports, permissions_reports)
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
