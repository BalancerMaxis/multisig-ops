import json
from dotmap import DotMap
from datetime import date
from os import listdir
from os.path import isfile, join
from great_ape_safe import GreatApeSafe
from web3 import Web3
from helpers.addresses import r
from pandas import pandas as pd
from brownie import interface

dont_sweep_tokens = ["0xa718042E5622099E5F0aCe4E7122058ab39e1bbe".lower(),# TEMPLE/bbe
                     "0xB5E3de837F869B0248825e0175DA73d4E8c3db6B".lower(), # RETH/bbeusd]
                     "0x50Cf90B954958480b8DF7958A9E965752F627124".lower(), # bb-e-usd
                     "0x4fD4687ec38220F805b6363C3c1E52D0dF3B5023".lower(), # wstETH/b-e-usd
                    ]

swap_to_bal_tokens = [r.tokens.AURABAL, r.tokens.BalWeth8020]
force_sweep_tokens = ["0xd33526068d116ce69f19a9ee46f0bd304f21a51f".lower()] # RPL
target_file = "../../../FeeSweep/2023-03-17-eth.json" ## Mainnet only
target_dir = "../../../FeeSweep" ## For reports


today = str(date.today())

# The input data is sometimes rounded.  amount - dust_factor/amount is swept.  Larger dust factor = less dust
dust_factor = 1000000

def setupSafe(address=r.balancer.multisigs.fees):
    safe = GreatApeSafe(r.balancer.multisigs.fees)
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
        if address in dont_sweep_tokens:
            continue
        if usd_value > sweep_limit or address in force_sweep_tokens:
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


def claimFees(safe, sweeps):
    print("Sweeping fees")
    address_list = list(sweeps.keys())
    amounts_list = list(sweeps.values())
    sweeper = safe.contract(r.balancer.ProtocolFeesWithdrawer)
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
            safe.cow.market_sell(
                asset_sell=asset,
                asset_buy=to_token,
                mantissa_sell=amount,
                deadline=60*60*4, ## 4 hours
                chunks=1, # Use to break up large trades, if used more tha one resulting trade uid is returned.
                coef=0.99 # Use to define slippage, this is multipled by the quoted market price to define min price.
            )
            results.append([str(asset.symbol()), str(asset.address), float(amount/10**asset.decimals()), str(result)])
        except:
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
    usd = safe.contract(r.tokens.bb_a_usd)
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
    safe=setupSafe(r.balancer.multisigs.fees)
    sweeps=generateSweepFile(safe, target_file)
    claimFees(safe, sweeps)
    cowswapFees(safe, sweeps)
    safe.post_safe_tx(gen_tenderly=False)

if __name__ == "__main__":
    main()


