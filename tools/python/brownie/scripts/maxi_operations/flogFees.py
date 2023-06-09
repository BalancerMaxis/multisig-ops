import json
from dotmap import DotMap
from datetime import date
from os import listdir
from os.path import isfile, join
from great_ape_safe import GreatApeSafe
from web3 import Web3
from bal_addresses import AddrBook
from pandas import pandas as pd
from brownie import interface

a = AddrBook("mainnet")
r = a.dotmap
monorepo_addys_by_chain = a.reversebook
sweep_limit = 5000
today = str(date.today())

dont_sweep_tokens = []

swap_to_bal_tokens = [r.tokens.AURABAL.lower(), r.tokens.BalWeth8020.lower()]
force_sweep_tokens = []
target_file = f"../../../FeeSweep/{today}-eth.json" ## Mainnet only
target_dir = "../../../FeeSweep" ## For reports



# The input data is sometimes rounded.  amount - dust_factor/amount is swept.  Larger dust factor = less dust
dust_factor = 1000000

def setupSafe(address=r.multisigs.fees):
    safe = GreatApeSafe(address)
    safe.init_cow(prod=True)  ## Set prod=true to not load swaps up on the staging cowswap interface (barn.cowswap.fi)
    return safe

def generateSweepFile(sourcefile):
    # sweeps is a map with addresses as keys and sweep amounts as values
    sweeps = {}
    report = ""
    total = 0
    with open(sourcefile, "r") as f:
        data = json.load(f)
    chain = data[0]["chain"]
    for feeData in data:
        symbol = feeData["symbol"]
        address = feeData["id"]
        rounded_raw_amount = int(feeData["raw_amount"])
        raw_amount = int(rounded_raw_amount - rounded_raw_amount/dust_factor)
        amount = feeData["amount"]
        rounded_amount = "{:.4f}".format(amount)
        price = feeData["price"]
        usd_value = int(amount) * price
        if address in dont_sweep_tokens:
            continue
        if usd_value > sweep_limit or address in force_sweep_tokens:
            sweeps[address] = raw_amount
            report += f"Sweep {rounded_amount} of {symbol}({address}) worth ${usd_value}\n"
            total += usd_value
    report += f"\n>>>Total USD Value of sweeps at time of input json: ${total}"
    print(report)

    with open(f"{target_dir}/out/{today}-{chain}.report.txt", "w") as f:
        f.write(report)
    return sweeps


def claimFees(safe, sweeps):
    print("Sweeping fees")
    address_list = list(sweeps.keys())
    amounts_list = list(sweeps.values())
    sweeper = safe.contract(a.flatbook["20220517-protocol-fee-withdrawer/ProtocolFeesWithdrawer"])
    sweeper.withdrawCollectedFees(address_list, amounts_list, safe.address)

def cowswapFees(safe, sweeps):
    print("Setting up cowswap orders")
    error_tokens = []
    results = []
    usd = safe.contract(r.tokens.USDC)
    bal = safe.contract(r.tokens.BAL)
    for address, amount in sweeps.items():
        if Web3.toChecksumAddress(address) == r.tokens.BAL or Web3.toChecksumAddress(address) == r.tokens.USDC:
            ## Don't sell BAL or USDC
            continue
        asset = safe.contract(address, Interface=interface.ERC20)
        if address in swap_to_bal_tokens:
            to_token = bal
        else:
            to_token = usd
        try:
            result = safe.cow.market_sell(
                asset_sell=asset,
                asset_buy=to_token,
                mantissa_sell=amount,
                deadline=60*60*8, ## 4 hours
                chunks=1, # Use to break up large trades, if used more tha one resulting trade uid is returned.
                coef=0.96 # Use to define slippage, this is multipled by the quoted market price to define min price.
            )
            results.append([str(asset.symbol()), str(asset.address), float(amount/10**asset.decimals()), str(result)])
        except:
            if asset.address not in dont_sweep_tokens:
                print(f"Problems processing: {asset.address}")
                error_tokens.append(asset.address)

    ## Generate Report
    try:
        print(results)
        df = pd.DataFrame(results, columns=["Symbol", "Address", "Amount", "Cowswap ID"])
        print(df.to_markdown())
        with open(f"{target_dir}/out/{today}-cowswap.md", "w") as f:
            df.to_markdown(buf=f)
    except:
        print("Error generating report, skipping")
    if len(error_tokens) > 0:
        print(f"The following tokens had problems and may not show up to be traded: {error_tokens}")

def payFees(safe, half=True):
    distrbutor = safe.contract(r.balancer.feeDistributor)
    usd = safe.contract("0xfebb0bbf162e64fb9d0dfe186e517d84c395f016") ## bb-a-usd v3
    bal = safe.contract(r.tokens.BAL)
    safe.take_snapshot([bal, usd])
    if half:
        print("Paying half the remaining USDC and BAL balances as fees to veBAL.  This should be a fee sweep week.")
        bal_amount = bal.balanceOf(safe.address)/2
        usd_amount = usd.balanceOf(safe.address)/2
    else:
        print("Paying ALL of the remaining USDC and BAL balances as fees to veBAL.  This should be NO fee-sweep week.")
        bal_amount = bal.balanceOf(safe.address)
        usd_amount = usd.balanceOf(safe.address)
    assert bal_amount > 0,  " BAL has a balance of 0, both tokens require some balance for this script to work."
    assert usd_amount > 0,  " USD has a balance of 0, both tokens require some balance for this script to work."

    bal.approve(distrbutor.address, bal_amount)
    usd.approve(distrbutor.address, usd_amount)
    distrbutor.depositTokens([bal.address, usd.address],[bal_amount, usd_amount])
    safe.post_safe_tx(gen_tenderly=False)


def main():
    safe=setupSafe(r.multisigs.fees)
    sweeps=generateSweepFile(target_file)
    claimFees(safe, sweeps)
    cowswapFees(safe, sweeps)
    safe.post_safe_tx(gen_tenderly=False)

if __name__ == "__main__":
    main()


