from brownie import Contract, network
from helpers.addresses import r
from web3 import Web3
import json
import requests
from dotmap import DotMap
from prettytable import PrettyTable
import os

def dicts_to_table_string(dict_list, header=None):
    table = PrettyTable(header)
    for dict_ in dict_list:
        table.add_row(list(dict_.values()))
    table.align["pool_name"] = "l"
    table.align["function"] = "l"
    table.align["style"] = "l"
    return str(table)


def main(tx_builder_jsons=os.getenv('PAYLOAD_LIST')):
    outputs = []
    for payload in tx_builder_jsons:
        with open(payload, "r") as json_data:
            payload = json.load(json_data)
        tx_list = payload["transactions"]
        authorizer = Contract(r.balancer.authorizer_adapter)
        gauge_controller = Contract(r.balancer.gauge_controller)
        vault = Contract(r.balancer.vault)
        for transaction in tx_list:
            if transaction["contractMethod"]["name"] != "performAction":
                continue ## Not an Authorizer tx
            authorizer_target_contract = Web3.toChecksumAddress(transaction["contractInputsValues"]["target"])
            if authorizer_target_contract == gauge_controller:
                (command, inputs) = gauge_controller.decode_input(transaction["contractInputsValues"]["data"])
            else: # Kills are called directly on gauges, so assuming a json with gauge adds disables if it's not a gauge control it's a gauge.
                (command, inputs) = Contract(authorizer_target_contract).decode_input(transaction["contractInputsValues"]["data"])

            #print(command)
            #print(inputs)
            if len(inputs) == 0: ## Is a gauge kill
                gauge_type = "NA"
                gauge_address = transaction["contractInputsValues"]["target"]
            else:
                gauge_address = inputs[0]
                gauge_type = inputs[1]

            #if type(gauge_type) != int or gauge_type == 2: ## 2 is mainnet gauge
            #print(f"processing {gauge_address}")
            gauge = Contract(gauge_address)
            pool_token_list = []
            #print(gauge.selectors.values())
            fxSelectorToChain = {
                "getTotalBridgeCost": "arbitrum",
                "getPolygonBridge": "polygon",
                "getArbitrumBridge": "arbitrum",
                "getGnosisBridge": "gnosis",
                "getOptimismBridge": "optimism"
            }

            fingerprintFx = list(set(gauge.selectors.values()).intersection(list(fxSelectorToChain.keys())))
            if len(fingerprintFx) > 0:  ## Is sidechain
                l2 = fxSelectorToChain[fingerprintFx[0]]
                #print(l2, gauge.getRecipient())
                recipient = gauge.getRecipient()
                chain = f"{l2}-main"
                network.disconnect()
                network.connect(chain)
                l2hop1=Contract(recipient)
                ## Check if this is a new l0 style gauge
                if "reward_receiver" in l2hop1.selectors.values():  ## Old child chain streamer style
                    l2hop2=Contract(l2hop1.reward_receiver())
                    pool_name = f"{l2.upper()}: {l2hop2.name()}"
                    lp_token = l2hop2.lp_token()
                    style = "ChildChainStreamer"
                else: # L0 style
                    pool_name = f"{l2.upper()}: {l2hop1.name()}"
                    lp_token = l2hop1.lp_token()
                    style = "L0 sidechain"
                ## Go back to mainnet
                network.disconnect()
                network.connect("mainnet")
            elif "name" not in gauge.selectors.values():
                recipient = Contract(gauge.getRecipient())
                escrow = Contract(recipient.getVotingEscrow())
                pool_name =  escrow.name()
                lp_token = Contract(escrow.token()).name()
                style = "ve8020 Single Recipient"
            else:
                pool_name = gauge.name()
                lp_token = gauge.lp_token()
                style = "mainnet"

            outputs.append({
                "function": command,
                "gauge_address": gauge_address,
                "gauge_type": gauge_type,
                "pool_name": pool_name,
                "lp_token": lp_token,
                "style": style
            })

    print(dicts_to_table_string(outputs, outputs[0].keys()))


