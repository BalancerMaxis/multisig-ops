from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from web3 import Web3 as web3
import json
import requests
from dotmap import DotMap
from prettytable import PrettyTable

bridge_chain_map = {
    ""
}
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

def dicts_to_table_string(dict_list, header=None):
    table = PrettyTable(header)
    for dict_ in dict_list:
        table.add_row(list(dict_.values()))
    return str(table)

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
            (command, inputs) = gauge_controller.decode_input(transaction["contractInputsValues"]["data"])
        else: # Kills are called directly on gauges, so assuming a json with gauge adds disables if it's not a gauge control it's a gauge.
            (command, inputs) = safe.contract(authorizer_target_contract).decode_input(transaction["contractInputsValues"]["data"])

        print(command)
        print(inputs)
        if len(inputs) == 0: ## Is a gauge kill
            gauge_type = "NA"
            gauge_address = transaction["contractInputsValues"]["target"]
        else:
            gauge_address = inputs[0]
            gauge_type = inputs[1]

        #if type(gauge_type) != int or gauge_type == 2: ## 2 is mainnet gauge
        gauge = safe.contract(gauge_address)
        #print(f"processing {gauge} as a gauge with lp token {gauge.lp_token()}")
        pool_token_list = []
        if "getTotalBridgeCost" in gauge.selectors.values(): ## Is sidechain
            pool_name = "Sidechain Gauge"
            lp_token = f"Recipient: {gauge.getRecipient()}"
        else:
            pool_name = gauge.name()
            lp_token = gauge.lp_token()

        outputs.append({
            "function": command,
            "gauge_address": gauge_address,
            "gauge_type": gauge_type,
            "pool_name": pool_name,
            "lp_token": lp_token
        })
        #else:
        #    print(f"skipping non-mainnet gauge {gauge_address}")
        #    outputs.append({
        #        "function": command,
        #        "gauge_address": gauge_address,
        #        "gauge_type": gauge_type,
        #        "pool_name": "NA",
        #        "lp_token": "NA"
        #    })


    print(dicts_to_table_string(outputs, outputs[0].keys()))


