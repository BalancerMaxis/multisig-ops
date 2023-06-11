import os
from typing import Optional

from bal_addresses import AddrBook
from brownie import Contract
from brownie import network

from script_utils import get_changed_files

addr_book = AddrBook("mainnet")
flatbook = addr_book.flatbook

GAUGE_ADD_METHODS = ['gauge', 'rootGauge']
ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def _parse_gauge_adder_transaction(transaction: dict) -> Optional[dict]:
    if transaction['to'] != flatbook[addr_book.search_unique("v4/GaugeAdder")]:
        return
    # Find command and gauge address
    command = transaction["contractMethod"]["name"]
    for method in GAUGE_ADD_METHODS:
        gauge_address = transaction["contractInputsValues"].get(method)
        if gauge_address:
            break
    # TODO:


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
    """
    if not network.is_connected():
        network.connect("mainnet")
    outputs = []
    # gauge_controller = Contract(flatbook[addr_book.search_unique("GaugeController")])
    for file in files:
        print(f"Processing: {file}")
        tx_list = file["transactions"]
        for transaction in tx_list:
            data = _parse_gauge_adder_transaction(transaction)


def main() -> None:
    files = get_changed_files()
    added_gauges = handle_added_gauges(files)


if __name__ == "__main__":
    main()
