import json
from dotmap import DotMap
from datetime import date
from os import listdir
from os.path import isfile, join
from great_ape_safe import GreatApeSafe
from web3 import Web3
from helpers.addresses import r
from pandas import pandas as pd

fee_swap_target_token = r.tokens.bb_a_usd
target_file = "../../../FeeSweep/test-2023-02-10-eth.json" ## Mainnet only
target_dir = "../../../FeeSweep" ## For reports


safe = GreatApeSafe(r.balancer.multisigs.fees)
safe.init_cow(prod=True) ## Set prod=true to not load swaps up on the staging cowswap interface (barn.cowswap.fi)

today = str(date.today())

# The input data is sometimes rounded.  amount - dust_factor/amount is swept.  Larger dust factor = less dust
dust_factor = 100000000
def generateSweepFile(sourcefile):
    # sweeps is a map with addresses as keys and sweep amounts as values
    sweeps = {}
    report = ""
    total = 0
    with open(sourcefile, "r") as f:
        data = json.load(f)
    chain = data[0]["chain"]
    if chain == "eth":
        sweep_limit = 10000
    else:
        sweep_limit = 5000
    for feeData in data:
        symbol = feeData["symbol"]
        address = feeData["id"]
        rounded_raw_amount = int(feeData["raw_amount"])
        raw_amount = int(rounded_raw_amount - rounded_raw_amount/dust_factor)
        amount = feeData["amount"]
        rounded_amount = "{:.4f}".format(amount)
        price = feeData["price"]
        usd_value = int(amount) * price
        if usd_value > sweep_limit:
            sweeps[address] = raw_amount
            report += f"Sweep {rounded_amount} of {symbol}({address}) worth ${usd_value}\n"
            total += usd_value
    report += f"\n>>>Total USD Value of sweeps at time of input json: ${total}"
    print(report)

    # Generate JSON
    with open(target_file, "r") as f:
        tx_builder = json.load(f)
    tx_out_map = DotMap(tx_builder)
    # TX builder wants lists in a string, addresses unquoted, and large integers without e+
    tx_out_map.transactions[0].contractInputsValues.tokens = str(list(sweeps.keys())).replace("'", "")
    tx_out_map.transactions[0].contractInputsValues.amounts = str(list(sweeps.values()))
    with open(f"{target_dir}/out/{today}-{chain}.json", "w") as f:
        json.dump(dict(tx_out_map), f)
    with open(f"{target_dir}/out/{today}-{chain}.report.txt", "w") as f:
        f.write(report)
    return sweeps


def claimFees(sweeps):
    print("Sweeping fees")
    address_list = list(sweeps.keys())
    safe.take_snapshot(address_list)
    amounts_list = list(sweeps.values())
    sweeper = safe.contract(r.balancer.ProtocolFeesWithdrawer)
    sweeper.withdrawCollectedFees(address_list, amounts_list, safe.address)
    safe.print_snapshot()

def flogFees(sweeps):
    print("Setting up cowswap orders")
    results = []
    usd = safe.contract(fee_swap_target_token)
    for address, amount in sweeps.items():
        if Web3.toChecksumAddress(address) == r.tokens.BAL:
            ## Don't sell BAL
            continue
        asset = safe.contract(address)
        result = safe.cow.market_sell(
            asset_sell=asset,
            asset_buy=usd,
            mantissa_sell=amount,
            deadline=60*60*4, ## 4 hours
            chunks=1, # Use to break up large trades
            coef=0.995 # Use to define slippage, this is multipled by the quoted market price to define min price
        )
        results.append([asset.symbol(), asset.address, amount/10**asset.decimals(), result])

    ## Generate Report
    results.reverse() ## To match cowswap ordering

    df = pd.DataFrame(results, columns=["Symbol", "Address", "Amount", "Cowswap ID"])
    print(df.to_markdown())
    with open(f"{target_dir}/out/{today}-cowswap.md", "w") as f:
        df.to_markdown(buf=f)

def payFees(half=True):
    distrbutor = safe.contract(r.balancer.feeDistributor)
    usd = safe.contract(r.tokens.USDC)
    bal = safe.contract(r.tokens.BAL)
    safe.take_snapshot([bal, usd])
    if half:
        bal_amount = bal.balanceOf(safe.address)/2
        usd_amount = usd.balanceOf(safe.address)/2
    else:
        bal_amount = bal.balanceOf(safe.address)
        usd_amount = usd.balanceOf(safe.address)
    assert bal_amount > 0,  " BAL has a balance of 0, both tokens require some balance for this script to work."
    assert usd_amount > 0,  " USD has a balance of 0, both tokens require some balance for this script to work."

    bal.approve(distrbutor.address, bal_amount)
    usd.approve(distrbutor.address, usd_amount)
    distrbutor.depositTokens([bal.address, usd.address],[bal_amount, usd_amount])
    safe.post_safe_tx(gen_tenderly=False)

def main():
    sweeps=generateSweepFile(target_file)
    claimFees(sweeps)
    flogFees(sweeps)
    safe.post_safe_tx(gen_tenderly=False)

if __name__ == "__main__":
    main()


