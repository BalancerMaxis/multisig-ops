import json
from dotmap import DotMap
from datetime import date
from os import listdir
from os.path import isfile, join

### Whitelist tokens are swept every run regardless of min amount.
whitelist_tokens = []

today = str(date.today())
target_dir = "../../FeeSweep"
# The input data is sometimes rounded.  amount - dust_factor/amount is swept.  Larger dust factor = less dust
dust_factor = 1


def generateSweepFile(sourcefile):
    # sweeps is a map with addresses as keys and sweep amounts as values
    pct_to_sweep = 0.05
    sweeps = {}
    report = ""
    total = 0
    with open(sourcefile, "r") as f:
        data = json.load(f)
    chain = data[0]["chain"]
    sweep_limit = 0
    for feeData in data:
        symbol = feeData["symbol"]
        address = feeData["id"]
        rounded_raw_amount = int(feeData["raw_amount"] * pct_to_sweep)
        raw_amount = int(rounded_raw_amount)
        amount = feeData["amount"] * pct_to_sweep
        rounded_amount = "{:.4f}".format(amount)
        price = feeData["price"]
        usd_value = int(amount) * price
        if raw_amount > 0:
            sweeps[address] = raw_amount
            report += (
                f"Sweep {rounded_amount} of {symbol}({address}) worth ${usd_value}\n"
            )
            total += usd_value
        else:
            print(f"skipping {symbol} with amount {amount}")
    report += f"\n>>>Total USD Value of sweeps at time of input json: ${total}"
    print(report)

    # Generate JSON
    with open(f"{target_dir}/feeSweep.json", "r") as f:
        tx_builder = json.load(f)
    tx_out_map = DotMap(tx_builder)
    # TX builder wants lists in a string, addresses unquoted, and large integers without e+
    tx_out_map.transactions[0].contractInputsValues.tokens = str(
        list(sweeps.keys())
    ).replace("'", "")
    tx_out_map.transactions[0].contractInputsValues.amounts = str(list(sweeps.values()))
    tx_out_map.transactions[
        0
    ].contractInputsValues.recipient = (
        "0x7f4b5250C63E24360055342D2a4427079290F044"  ## Mimic mock withdrawer (op)
    )
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
