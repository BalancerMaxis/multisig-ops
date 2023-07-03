from typing import Optional

from bal_addresses import AddrBook
from brownie import Contract
from brownie import network
from web3 import Web3

from .script_utils import format_into_report
from .script_utils import get_changed_files
from .script_utils import get_pool_info
from .script_utils import merge_files

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


def _parse_added_transaction(transaction: dict) -> Optional[dict]:
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
    if transaction['to'] != FLATBOOK[ADDR_BOOK.search_unique("v4/GaugeAdder")]:
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
        "pool_id": pool_id,
        "symbol": pool_symbol,
        "pool_address": pool_address,
        "aFactor": a_factor,
        "gauge_address": gauge_address,
        "fee": f"{fee}%",
        "cap": gauge_cap,
        "style": style,
        "chain": chain if chain else "mainnet",
    }


def _parse_removed_transaction(transaction: dict) -> Optional[dict]:
    if network.is_connected():
        network.disconnect()
    network.connect(CHAIN_MAINNET)
    encoded_data = transaction["contractInputsValues"].get("data")
    if not encoded_data:
        print("No encoded data found! Not a gauge kill transaction")
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
        "pool_id": pool_id,
        "symbol": pool_symbol,
        "pool_address": pool_address,
        "aFactor": a_factor,
        "gauge_address": gauge_address,
        "fee": f"{fee}%",
        "cap": gauge_cap,
        "style": style,
        "chain": chain if chain else "mainnet",
    }


def handle_added_gauges(files: list[dict]) -> dict[str, str]:
    """
    Function that parses transaction list and tries to collect following data about added
    gauges:
    - pool_id
    - symbol
    - pool_address
    - aFactor
    - gauge_address
    - cap
    - fee
    - style

    Then it converts collected data into a formatted list of strings.
    """
    reports = {}
    for file in files:
        outputs = []
        print(f"Processing: {file['file_name']}")
        tx_list = file["transactions"]
        for transaction in tx_list:
            data = _parse_added_transaction(transaction)
            if data:
                outputs.append(data)

        if outputs:
            reports[file['file_name']] = format_into_report(file, outputs)
    return reports


def handle_removed_gauges(files: list[dict]) -> dict[str, str]:
    """
    Function that parses transaction list and tries to collect data about removed gauges.
    Format is the same as in handle_added_gauges.
    """
    reports = {}
    for file in files:
        outputs = []
        print(f"Processing: {file['file_name']}")
        tx_list = file["transactions"]
        for transaction in tx_list:
            data = _parse_removed_transaction(transaction)
            if data:
                outputs.append(data)
        if outputs:
            reports[file['file_name']] = format_into_report(file, outputs)
    return reports


def main() -> None:
    files = get_changed_files()
    print(f"Found {len(files)} files with added/removed gauges")
    # TODO: Add here more handlers for other types of transactions
    added_gauges = handle_added_gauges(files)
    removed_gauges = handle_removed_gauges(files)

    merged_files = merge_files(added_gauges, removed_gauges)
    # Save report to report.txt file
    with open("output.txt", "w") as f:
        for report in merged_files.values():
            f.write(report)
    for filename, report in merged_files.items():
        # Replace .json with .report.txt
        filename = filename.replace(".json", ".report.txt")
        with open(f"../../{filename}", "w") as f:
            f.write(report)


if __name__ == "__main__":
    main()
