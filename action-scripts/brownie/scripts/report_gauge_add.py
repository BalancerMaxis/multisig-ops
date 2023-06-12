import os
from typing import Optional

from bal_addresses import AddrBook
from brownie import Contract
from brownie import network
from brownie.exceptions import VirtualMachineError
from web3 import Web3

from .script_utils import convert_output_into_table
from .script_utils import get_changed_files
from .script_utils import get_pool_info

addr_book = AddrBook("mainnet")
flatbook = addr_book.flatbook

GAUGE_ADD_METHODS = ['gauge', 'rootGauge']
ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

STYLE_MAINNET = "Mainnet"
STYLE_SINGLE_RECIPIENT = "Single Recipient"
STYLE_CHILD_CHAIN_STREAMER = "ChildChainStreamer"
SELECTOR_MAP = {
    "getTotalBridgeCost": "arbitrum",
    "getPolygonBridge": "polygon",
    "getArbitrumBridge": "arbitrum",
    "getGnosisBridge": "gnosis",
    "getOptimismBridge": "optimism"
}


def _parse_gauge_adder_transaction(transaction: dict) -> Optional[dict]:
    """
    Parse a gauge adder transaction and return a dict with parsed data.

    First, it tries to extract gauge address from the transaction data.
    If it fails, it tries to extract gauge address from the transaction input.

    Then, it extracts gauge data from mainnet or jump to sidechains if needed.

    :param transaction: transaction to parse
    :return: dict with parsed data
    """
    network.disconnect()
    network.connect("mainnet")
    if transaction['to'] != flatbook[addr_book.search_unique("v4/GaugeAdder")]:
        return

    # Parse only gauge add transactions
    if not any(method in transaction["contractInputsValues"] for method in GAUGE_ADD_METHODS):
        return
    # Find command and gauge address
    command = transaction["contractMethod"]["name"]
    gauge_address = None
    for method in GAUGE_ADD_METHODS:
        gauge_address = transaction["contractInputsValues"].get(method)
        if gauge_address:
            break
    # If no gauge address found, try to extract it from the encoded data
    if not gauge_address:
        target_contract = Web3.toChecksumAddress(
            transaction["contractInputsValues"]["target"]
        )
        try:
            (command, inputs) = Contract(target_contract).decode_input(
                transaction["contractInputsValues"]["data"])
        except (VirtualMachineError, Exception):
            print(f"Failed to decode input for transaction: {transaction}")
            return
        gauge_address = inputs[0]
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
    intersection_selector = list(set(gauge_selectors).intersection(list(SELECTOR_MAP.keys())))
    if len(intersection_selector) > 0:  # Is sidechain
        chain = SELECTOR_MAP[intersection_selector[0]]
        recipient = gauge.getRecipient()
        network.disconnect()
        network.connect(f"{chain}-main")
        sidechain_recipient = Contract(recipient)
        if "reward_receiver" in sidechain_recipient.selectors.values():
            sidechain_recipient = Contract(sidechain_recipient.reward_receiver())
        pool_name, pool_symbol, pool_id, pool_address, a_factor, fee = get_pool_info(
            sidechain_recipient.lp_token())
        style = STYLE_CHILD_CHAIN_STREAMER
    elif "name" not in gauge_selectors:
        recipient = Contract(gauge.getRecipient())
        escrow = Contract(recipient.getVotingEscrow())
        pool_name, pool_symbol, pool_id, pool_address, a_factor, fee = get_pool_info(escrow.token())
        style = STYLE_SINGLE_RECIPIENT
    else:
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


def handle_added_gauges(files: list[dict]) -> list:
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
    reports = []
    for file in files:
        outputs = []
        print(f"Processing: {file['file_name']}")
        tx_list = file["transactions"]
        for transaction in tx_list:
            data = _parse_gauge_adder_transaction(transaction)
            if data:
                outputs.append(data)
        if not outputs:
            continue
        file_report = f"File name: {file['file_name']}\n"
        file_report += f"COMMIT: `{os.getenv('COMMIT_SHA', 'N/A')}`\n"
        file_report += "```\n"
        file_report += convert_output_into_table(
            outputs, list(outputs[0].keys())
        )
        file_report += "\n```\n"
        reports.append(file_report)
    return reports


def main() -> None:
    files = get_changed_files()
    print(f"Found {len(files)} files with added gauges")
    added_gauges = handle_added_gauges(files)
    # Save report to report.txt file
    with open("output.txt", "w") as f:
        for report in added_gauges:
            f.write(report)


if __name__ == "__main__":
    main()
