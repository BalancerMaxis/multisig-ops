from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from web3 import Web3
import json
import requests
from dotmap import DotMap
from prettytable import PrettyTable
import sys
import os
from polygonscan import PolygonScan


# USAGE: Use like: brownie run scripts/maxi_operations/get_gauge_mappings.py parse_json ../../../BIPs/BIP-184-185-186-187-188.json
# USAGE: Use from: The root brownie directory - ../../ from where this file sits

### This script was built for BIP-177.  It's an example of how to map gauges to pool names and addresses
### In this case it pulls in tx builder json files that contain gauge adds and removes through the authorizer and builds a
### table includes function, guage, pool address and gauge name.

INFURA_KEY  = os.getenv('WEB3_INFURA_PROJECT_ID')

w3eth = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_KEY}"))
w3arbitrum = Web3(Web3.HTTPProvider(f"https://arbitrum-mainnet.infura.io/v3/{INFURA_KEY}"))
w3optimism = Web3(Web3.HTTPProvider(f"https://optimism-mainnet.infura.io/v3/{INFURA_KEY}"))
w3polygon = Web3(Web3.HTTPProvider(f"https://polygon-mainnet.infura.io/v3/{INFURA_KEY}"))

w3_by_chain_id = {
    1: w3eth,
    42161: w3arbitrum,
    137: w3polygon,
    10: w3optimism
}

def follow_offchain_gauge(gauge, chain_id):
    outputs = {}
    print(w3_by_chain_id[chain_id].isConnected())
    crosschain_streamer = w3_by_chain_id[chain_id].eth.contract(address=gauge.getRecipient(),
                                                                abi=json.load(open("abis/IChildChainStreamer.json")))
    print(crosschain_streamer.address)
    crosschain_streamer.functions.reward_count().call()
    gauge_address = crosschain_streamer.functions.reward_receiver().call()
    gauge = w3arbitrum.eth.contract(address=gauge_address, abi=json.load(open("abis/IRewardsOnlyGauge.json")))
    output = {
        "name": gauge.functions.name().call(),
        "address": gauge.address
    }
    return output


def dicts_to_table_string(dict_list, header=None):

    table = PrettyTable(header)
    for dict_ in dict_list:
        table.add_row(list(dict_.values()))
    return str(table)

def parse_json(tx_builder_json="../../../BIPs/BIP-189/BIP-189B.json"):
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
        authorizer_target_contract = Web3.toChecksumAddress(transaction["contractInputsValues"]["target"])
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
        if "getTotalBridgeCost" in gauge.selectors.values(): ## Is sidechain/arbitrum?
            offchain = follow_offchain_gauge(gauge, 42161)
            pool_name = f'ARBI: (${offchain["name"]}',
            lp_token = offchain["address"]
        elif "getPolygonBridge" in gauge.selectors.values():
            print("polygon")
            offchain = follow_offchain_gauge(gauge, 137)
            pool_name = f'MATIC: (${offchain["name"]}',
            lp_token = offchain["address"]
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

if __name__ == "__main__":
    parse_json(sys.argv[0])
