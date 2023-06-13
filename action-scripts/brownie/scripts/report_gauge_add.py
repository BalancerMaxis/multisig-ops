import os
from typing import Optional

from bal_addresses import AddrBook
from brownie import Contract
from brownie import network

from .script_utils import format_into_report
from .script_utils import get_changed_files
from .script_utils import get_pool_info

ADDR_BOOK = AddrBook("mainnet")
FLATBOOK = ADDR_BOOK.flatbook

GAUGE_ADD_METHODS = ['gauge', 'rootGauge']

STYLE_MAINNET = "Mainnet"
STYLE_SINGLE_RECIPIENT = "Single Recipient"
STYLE_CHILD_CHAIN_STREAMER = "ChildChainStreamer"

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


def _parse_added_transaction(transaction: dict) -> Optional[dict]:
    """
    Parse a gauge adder transaction and return a dict with parsed data.

    First, it tries to extract gauge address from the transaction data.
    If it fails, it tries to extract gauge address from the transaction input.

    Then, it extracts gauge data from mainnet or jump to sidechains if needed.

    :param transaction: transaction to parse
    :return: dict with parsed data
    """
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

    # Finally, extract gauge data from mainnet or jump to sidechains if needed
    gauge = Contract(gauge_address)
    gauge_selectors = gauge.selectors.values()
    gauge_cap = (
        f"{gauge.getRelativeWeightCap() / 10 ** 16}%"
        if "getRelativeWeightCap" in gauge_selectors else "N/A"
    )
    # Process sidechain gauges
    if chain != CHAIN_MAINNET:
        recipient = gauge.getRecipient()
        network.disconnect()
        network.connect(chain)
        sidechain_recipient = Contract(recipient)
        if "reward_receiver" in sidechain_recipient.selectors.values():
            sidechain_recipient = Contract(sidechain_recipient.reward_receiver())
        pool_name, pool_symbol, pool_id, pool_address, a_factor, fee = get_pool_info(
            sidechain_recipient.lp_token())
        style = STYLE_CHILD_CHAIN_STREAMER
    elif "name" not in gauge_selectors:  # Process single recipient gauges
        recipient = Contract(gauge.getRecipient())
        escrow = Contract(recipient.getVotingEscrow())
        pool_name, pool_symbol, pool_id, pool_address, a_factor, fee = get_pool_info(escrow.token())
        style = STYLE_SINGLE_RECIPIENT
    else:  # Process mainnet gauges
        (pool_name, pool_symbol, pool_id, pool_address, a_factor, fee) = get_pool_info(
            gauge.lp_token())
        style = STYLE_MAINNET

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


def main() -> None:
    files = get_changed_files()
    print(f"Found {len(files)} files with added gauges")
    # TODO: Add here more handlers for other types of transactions
    added_gauges = handle_added_gauges(files)
    # Save report to report.txt file
    with open("output.txt", "w") as f:
        for report in added_gauges.values():
            f.write(report)
    for filename, report in added_gauges.items():
        # Replace .json with .report.txt
        filename = filename.replace(".json", ".report.txt")
        with open(f"../../{filename}", "w") as f:
            f.write(report)


if __name__ == "__main__":
    main()
