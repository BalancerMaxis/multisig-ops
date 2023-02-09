from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from web3 import Web3 as web3
import json
import requests
from dotmap import DotMap
import pandas as pd

gauges_to_check = {
    "POLY: Balancer 20USDC-40TEL-40DFX RewardGauge Deposit":   "0xb61014De55A7AB12e53C285d88706dca2A1B7625",
    "Balancer NWWP Gauge Deposit (NOTE/WETH 50/50)":   "0x96d7e549eA1d810725e4Cd1f51ed6b4AE8496338",
    "Balancer 50N/A-50N/A Gauge Deposit (D2D/BAL 50/50)":   "0xf46FD013Acc2c6988BB2f773bd879101eB5d4573",
    "Balancer 20DAI-80TCR Gauge Deposit":   "0xAde9C0054f051f5051c4751563C7364765Bf52f5",
    "Balancer 20WETH-80HAUS Gauge Deposit":   "0x00Ab79a3bE3AacDD6f85C623f63222A07d3463DB",
    "ARBI: Balancer B-80PICKLE-20WETH RewardGauge Deposit":   "0x231B05F3a92d578EFf772f2Ddf6DacFFB3609749",
    "ARBI: Balancer 20WETH-80CRE8R RewardGauge Deposit":   "0x077794c30AFECcdF5ad2Abc0588E8CEE7197b71a",
    "POLY: Balancer TELX-60TEL-20BAL-20USDC RewardGauge Deposit":   "0x7C56371077fa0dD8327E5C53Ee26a37D14b671ad",
    "POLY: Balancer TELX-50TEL-50BAL RewardGauge Deposit":   "0xe0779Dc81B5DF4D421044f7f7227f7e2F5b0F0cC",
    ## The one below is already disabled and is a test
    "ARBI: Balancer 80MAGIC-20WETH RewardGauge Deposit": "0x785F08fB77ec934c01736E30546f87B4daccBe50",
}



def main(tx_builder_json="./testdata.json"):
    outputs = []
    with open(tx_builder_json, "r") as json_data:
        payload = json.load(json_data)
    tx_list = payload["transactions"]
    safe = GreatApeSafe(r.balancer.multisigs.dao)
    authorizer = safe.contract(r.balancer.authorizer_adapter)
    gauge_controller = safe.contract(r.balancer.gauge_controller)
    vault = safe.contract(r.balancer.vault)
    for transaction in tx_list:
        if transaction["contractMethod"]["name"] != "performAction":
            continue ## Not an Authorizer tx
        authorizer_target_contract = web3.toChecksumAddress(transaction["contractInputsValues"]["target"])
        if authorizer_target_contract == gauge_controller:
            # Example output of decode_input on gauge_adds
            # `('add_gauge(address,int128)', ['0xA2a9Ebd6f4dEA4802083F2C8D08066A4e695e64B', 2])
            (command, inputs) = gauge_controller.decode_input(transaction["contractInputsValues"]["data"])
            if inputs[1] == 2:
                gauge = safe.contract(inputs[0])
                print(f"processing {gauge} as a gauge with lp token {gauge.lp_token()}")
                pool_token_list = []
                outputs.append({
                    "function:": command,
                    "gauge_address": inputs[0],
                    "gauge_type": inputs[1],
                    "pool_name": str(gauge.name()),
                    "lp_token": str(gauge.lp_token())
                })
            else:
                print(f"skipping non-mainnet gauge {inputs[0]}")
                outputs.append({
                    "function": command,
                    "gauge_address": inputs[0],
                    "gauge_type": inputs[1],
                    "pool_name": "NA",
                    "lp_token": "NA"
                })
    df = pd.DataFrame(outputs)
    print(df.to_markdown(index=False))

