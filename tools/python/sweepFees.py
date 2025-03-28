import json
from dotmap import DotMap
from datetime import date
from os import listdir
from os.path import isfile, join
from bal_addresses import AddrBook

### Whitelist tokens are swept every run regardless of min amount.
whitelist_tokens = []

today = str(date.today())
target_dir = "../../FeeSweep"
# The input data is sometimes rounded.  amount - dust_factor/amount is swept.  Larger dust factor = less dust
dust_factor = 10000


def generateSweepFile(sourcefile):
    # sweeps is a map with addresses as keys and sweep amounts as values
    sweeps = {}
    report = ""
    total = 0
    with open(sourcefile, "r") as f:
        data = json.load(f)
    chain = data[0]["chain"]
    if chain == "avax":
        chain = "avalanche"
    if chain == "eth":
        chain = "mainnet"
    if chain == "pze":
        chain = "zkevm"
    print(chain)
    a = AddrBook(chain)
    if chain == "mainnet":
        sweep_limit = 500
    else:
        sweep_limit = 100
    for feeData in data:
        symbol = feeData["symbol"]
        address = feeData["id"]
        rounded_raw_amount = int(feeData["raw_amount"])
        raw_amount = int(rounded_raw_amount - rounded_raw_amount / dust_factor)
        amount = feeData["amount"]
        rounded_amount = "{:.4f}".format(amount)
        price = feeData["price"]
        usd_value = int(amount) * price
        if usd_value > sweep_limit or address in whitelist_tokens:
            sweeps[address] = raw_amount
            report += (
                f"Sweep {rounded_amount} of {symbol}({address}) worth ${usd_value}\n"
            )
            total += usd_value
    report += f"\n>>>Total USD Value of sweeps at time of input json: ${total}"
    print(report)

    # Generate JSON
    with open(f"{target_dir}/feeSweep.json", "r") as f:
        tx_builder = json.load(f)
    tx_out_map = DotMap(tx_builder)
    # TX builder wants lists in a string, addresses unquoted, and large integers without e+
    tx_out_map.transactions[0].to = a.search_unique("FeesWithdraw").address

    tx_out_map.transactions[0].contractInputsValues.tokens = str(
        list(sweeps.keys())
    ).replace("'", "")
    tx_out_map.transactions[0].contractInputsValues.amounts = str(list(sweeps.values()))
    with open(f"{target_dir}/out/{today}-{chain}.json", "w") as f:
        json.dump(dict(tx_out_map), f)
        f.write("\n")
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
