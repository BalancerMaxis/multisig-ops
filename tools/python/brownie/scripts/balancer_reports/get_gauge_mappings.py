from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from web3 import Web3 as web3
import json
import requests
from dotmap import DotMap
from prettytable import PrettyTable

### This script was built for BIP-177.  It's an example of how to map gauges to pool names and addresses
### In this case it pulls in tx builder json files that contain gauge adds and removes through the authorizer and builds a
### table includes function, guage, pool address and gauge name.
def dicts_to_table_string(dict_list, header=None):
    table = PrettyTable(header)
    for dict_ in dict_list:
        table.add_row(list(dict_.values()))
    return str(table)

def main(tx_builder_json="../../../BIPs/BIP-222-223.json"):
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

        #print(command)
        #print(inputs)
        if len(inputs) == 0: ## Is a gauge kill
            gauge_type = "NA"
            gauge_address = transaction["contractInputsValues"]["target"]
        else:
            gauge_address = inputs[0]
            gauge_type = inputs[1]

        #if type(gauge_type) != int or gauge_type == 2: ## 2 is mainnet gauge
        gauge = safe.contract(gauge_address)
        print(f"processing {gauge}")
        pool_token_list = []
        #print(gauge.selectors.values())
        fxSelectorToChain = {
            "getTotalBridgeCost": "L2: Arbitrum",
            "getPolygonBridge": "sidechain: Polygon",
            "getArbitrumBridge": "L2: Arbitrum",
            "getGnosisBridge": "sidechain: Gnosis",
            "getOptimismBridge": "sidechain: Optimism"
        }
        sidechain = list(set(gauge.selectors.values()).intersection(list(fxSelectorToChain.keys())))
        if len(sidechain) > 0:
            pool_name = fxSelectorToChain[sidechain[0]]
            lp_token = f"Recipient: {gauge.getRecipient()}"
        elif "name" not in gauge.selectors.values():
            recipient = safe.contract(gauge.getRecipient())
            escrow = safe.contract(recipient.getVotingEscrow())
            pool_name =  escrow.name()
            lp_token = safe.contract(escrow.token()).name()
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


