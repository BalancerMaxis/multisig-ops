from typing import Optional

from bal_addresses import AddrBook
from brownie import Contract
from brownie import network
from web3 import Web3

from .script_utils import format_into_report
from .script_utils import get_changed_files
from .script_utils import get_pool_info
from .script_utils import merge_files

ADDRESSES_MAINNET = AddrBook("mainnet").reversebook
ADDRESSES_POLYGON = AddrBook("polygon").reversebook
ADDRESSES_ARBITRUM = AddrBook("arbitrum").reversebook
ADDRESSES_AVALANCHE = AddrBook("avalanche").reversebook
ADDRESSES_OPTIMISM = AddrBook("optimism").reversebook
ADDRESSES_GNOSIS = AddrBook("gnosis").reversebook
ADDRESSES_ZKEVM = AddrBook("zkevm").reversebook
# Merge all addresses into one dictionary
ADDRESSES = {**ADDRESSES_MAINNET, **ADDRESSES_POLYGON, **ADDRESSES_ARBITRUM, **ADDRESSES_AVALANCHE,
             **ADDRESSES_OPTIMISM, **ADDRESSES_GNOSIS, **ADDRESSES_ZKEVM}



## Todo add chainname and chain_id to invoked AddrBooks
def _parse_transfer(transaction: dict, chainbook: object, chain_name: str) -> Optional[dict]:
    """
    Parse an ERC-20 transfer transaction and return a dict with parsed data.

    Returns None if no transfers

    :param transaction: transaction to parse
    :param chainbook: An AddrBook object invoked on the current chain
    :return: dict with parsed data
    """

    # Parse only gauge add transactions
    if transaction["contractMethod"]["name"] != "transfer":
        return
    # Get input values
    token = Contract(transaction["to"])
    recipient_address =  transaction["contractInputsValues"].get("to")
    raw_amount = int(transaction["contractInputsValues"].get("value"))
    amount = raw_amount / 10 ** token.decimals()
    symbol = token.symbol()
    recipient_name  = chainbook.reversebook[recipient_address]
    return {
        "function": "transfer",
        "token_symbol": symbol,
        "recipient_name": recipient_name,
        "amount": amount,
        "token_address": token.address,
        "recipient_address": recipient_address,
        "raw_amount": raw_amount,
        "chain": chain_name
    }



def handle_transfers(files: list[dict]) -> dict[str, str]:
    """
    Function that parses transaction list and tries to collect following data about added
    gauges:
    - token
    - recipient_address
    - recipient_name
    - amount
    Then it converts collected data into a formatted list of strings.
    """
    reports = {}
    for file in files:
        outputs = []
        print(f"Processing: {file['file_name']}")
        chain_id = file["chainId"]
        for cname, cid in AddrBook.CHAIN_IDS_BY_NAME.items():
            if int(cid) == int(chain_id):
                chain_name = cname

        network.disconnect()
        if chain_name == "mainnet":
            network.connect(chain_name)
        elif chain_name == "avalanche":
            network.connect("avax-main")
        else:
            network.connect(f"{chain_name}-main")
        chainbook = AddrBook(chain_name)

        tx_list = file["transactions"]
        for transaction in tx_list:
            data = _parse_transfer(transaction, chainbook, chain_name)
            if data:
                outputs.append(data)

        if outputs:
            reports[file['file_name']] = format_into_report(file, outputs)
    return reports


def main() -> None:
    files = get_changed_files()
    merged_files = handle_transfers(files)

    # Save report to report.txt file
    with open("output.txt", "w") as f:
        for report in merged_files.values():
            f.write(report)
    for filename, report in merged_files.items():
        # Replace .json with .report.txt
        filename = filename.replace(".json", ".txreport.txt")
        with open(f"../../{filename}", "w") as f:
            f.write(report)


if __name__ == "__main__":
    main()
