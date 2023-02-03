from brownie import chain, web3
from web3 import Web3
#from great_ape_safe import GreatApeSafe
from helpers.addresses import r
import datetime
import json
from dotmap import DotMap
from datetime import date

today = date.today()
target_dir = "../../../Feeswap/"
def main():
    # sweeps is a map with addresses as keys and sweep amounts as values
    sweeps = {}
    report = ""
    with open(f"{target_dir}{today}.json", "r") as f:
        data = json.load(f)
    if chain.id == 1:
        sweep_limit = 10000
    else:
        sweep_limit = 5000
    for feeData in data:
        symbol = feeData["symbol"]
        if symbol == "BAL":
            continue
        address = feeData["id"]
        raw_amount = int(feeData["raw_amount"])
        amount = feeData["amount"]
        price = feeData["price"]
        usd_value = amount * price
        if usd_value > sweep_limit:
            sweeps[address] = raw_amount
            report += f"Sweep {amount} of {symbol}({address}) worth ${usd_value}\n"

    print(report)

    # Generate JSON
    with open(f"{target_dir}feeSweep.json", "r") as f:
        tx_builder = json.load(f)
    tx_out_map = DotMap(tx_builder)
    tx_out_map.chainId = chain.id
    # TX builder wants lists in a string, addresses unquoted, and large integers without e+
    tx_out_map.transactions[0].contractInputsValues.tokens = str(list(sweeps.keys())).replace("'", "")
    tx_out_map.transactions[0].contractInputsValues.amounts = str(list(sweeps.values()))
    with open(f"{target_dir}out/{today}.json", "w") as f:
        json.dump(dict(tx_out_map), f)
    with open(f"{target_dir}out/{today}.report.txt", "w") as f:
        f.write(report)






