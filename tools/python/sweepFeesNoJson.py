import json
from dotmap import DotMap
from datetime import date
from os import listdir
from os.path import isfile, join
from brownie import Contract, chain
from web3 import Web3


### Whitelist tokens are swept every run regardless of min amount.
whitelist_tokens = []

chain = chain.id

today = str(date.today())
target_dir = "../../FeeSweep"
# The input data is sometimes rounded.  amount - dust_factor/amount is swept.  Larger dust factor = less dust
dust_factor = 10000


def genSweepsFromTokenList(tokenlist, collector):
    sweeps = {}
    for address in tokenlist:
        address = Web3.toChecksumAddress(address)
        token = Contract.from_explorer(address)
        sweeps[address] = token.balanceOf(collector)
    return sweeps


def generateSweepFile(tokenlist):
    # sweeps is a map with addresses as keys and sweep amounts as values
    sweeps = {}
    report = ""
    total = 0
    sweeps = genSweepsFromTokenList(tokenlist, collector)
    # Generate JSON
    with open(f"{target_dir}/feeSweep.json", "r") as f:
        tx_builder = json.load(f)
    tx_out_map = DotMap(tx_builder)
    # TX builder wants lists in a string, addresses unquoted, and large integers without e+
    tx_out_map.transactions[0].contractInputsValues.tokens = str(
        list(sweeps.keys())
    ).replace("'", "")
    tx_out_map.transactions[0].contractInputsValues.amounts = str(list(sweeps.values()))
    with open(f"{target_dir}/out/{today}-{chain}.json", "w") as f:
        json.dump(dict(tx_out_map), f)
    with open(f"{target_dir}/out/{today}-{chain}.report.txt", "w") as f:
        f.write(report)


def main():
    sourcefiles = [f for f in listdir(target_dir) if isfile(join(target_dir, f))]
    for file in sourcefiles:
        if (today in file) & (".json" in file):
            print(f"\n\n--------- Processing {target_dir}{file} ---------\n")
            generateSweepFile(f"{target_dir}/{file}")


if __name__ == "__main__":
    main()
