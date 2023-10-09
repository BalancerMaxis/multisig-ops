import csv
import json
from copy import deepcopy

from web3 import Web3

CSV = "../../../BIPs/00batched/2023-w38/BIP-431-airdrop.csv"
JSON = "../../../BIPs/00batched/2023-w38/BIP-431-airdrop.json"
TX_TEMPLATE = "../tx_builder_templates/erc20_transfer.json"
BASE_TEMPLATE = "../tx_builder_templates/base.json"

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]


def main():
    web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))  # TODO: change to arb node

    csvfile = open(CSV, "r")
    txs = csv.reader(csvfile)
    with open(TX_TEMPLATE, "r") as jsonfile:
        tx_template = json.load(jsonfile)
    with open(BASE_TEMPLATE, "r") as jsonfile:
        payload = json.load(jsonfile)
    txlist = []
    for row in txs:
        token_address = row[1]
        token_contract = web3.eth.contract(
            address=Web3.toChecksumAddress(token_address), abi=ERC20_ABI
        )
        receiver = row[2]
        amount = float(row[3])
        print(token_address, amount)
        # token = Contract(token_address)
        raw_amount = int(amount * 10 ** token_contract.functions.decimals().call())
        tx_data = deepcopy(tx_template)
        tx_data["contractInputsValues"]["to"] = receiver
        tx_data["contractInputsValues"]["value"] = str(raw_amount)
        tx_data["to"] = token_address
        txlist.append(tx_data)
        print(tx_data)
    payload["transactions"] = txlist
    print(txlist)
    with open(JSON, "w") as output:
        json.dump(payload, output, indent=2)


if __name__ == "__main__":
    main()
