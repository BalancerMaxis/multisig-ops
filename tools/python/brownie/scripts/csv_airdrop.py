import csv
import json
from brownie import Contract

CSV="../../../BIPs/00batched/2023-w38/BIP-431-airdrop.csv"
JSON="../../../BIPs/00batched/2023-w38/BIP-431-airdrop.json"
TX_TEMPLATE="../tx_builder_templates/erc20_transfer.json"
BASE_TEMPLATE="../tx_builder_templates/base.json"

def main():
    csvfile = open(CSV, "r")
    txs = csv.reader(csvfile)
    with open(TX_TEMPLATE, "r") as jsonfile:
        tx_template = json.load(jsonfile)
    with open(BASE_TEMPLATE, "r") as jsonfile:
        payload =  json.load(jsonfile)
    txlist = []
    for row in txs:
        token_address= row[1]
        receiver = row[2]
        amount = float(row[3])
        print (token_address, amount)
        token = Contract(token_address)
        raw_amount = int(amount * 10**token.decimals())
        tx_data = tx_template
        tx_data["contractInputsValues"]["to"] = receiver
        tx_data["contractInputsValues"]["value"] = raw_amount
        tx_data["to"] = token_address
        txlist.append(tx_data)
        print(tx_data)
    payload["transactions"] = txlist
    print(txlist)
    with open(JSON, "w") as output:
        json.dump(payload, output, indent=2)