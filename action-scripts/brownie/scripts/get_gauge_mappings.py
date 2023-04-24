from brownie import Contract, network
from helpers.addresses import r
from web3 import Web3
import json
from prettytable import PrettyTable
import os
from urllib.request import urlopen
from pathlib import Path


debug = False

def dicts_to_table_string(dict_list, header=None):
    table = PrettyTable(header)
    for dict_ in dict_list:
        table.add_row(list(dict_.values()))
    table.align["pool_name"] = "l"
    table.align["function"] = "l"
    table.align["style"] = "l"
    return str(table)



def get_payload_list():
    github_repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    api_url = f'https://api.github.com/repos/{github_repo}/pulls/{pr_number}/files'
    if debug:
        print(f"api url: {api_url}")
    url = urlopen(api_url)
    pr_file_data = json.loads(url.read())

    changed_files = []
    for file_json in pr_file_data:
        filename = (file_json['filename'])
        if debug:
            print(filename)
        if "BIPs/" in filename and filename.endswith(".json"):
            changed_files.append(filename)
        if debug:
            print(f"Changed Files:{changed_files}")
    return changed_files



def process_file(filename):
        with open(filename, "r") as json_data:
            try:
                payload = json.load(json_data)
            except:
                print(f"{filename} is not proper json")
                return
        if "transactions" not in payload.keys():
            print(f"{filename} json deos not contain a list of transactions")
            return
        outputs = []
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

            print(f"processing {gauge_address}")
            gauge = Contract(gauge_address)
            pool_token_list = []
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
                    lp_token = Contract(l2hop2.lp_token())
                    style = "ChildChainStreamer"
                else: # L0 style
                    pool_name = f"{l2.upper()}: {l2hop1.name()}"
                    lp_token = Contract(l2hop1.lp_token())
                    style = "L0 sidechain"
                ## Go back to mainnet
                network.disconnect()
                network.connect("mainnet")
            elif "name" not in gauge.selectors.values():
                recipient = Contract(gauge.getRecipient())
                escrow = Contract(recipient.getVotingEscrow())
                pool_name =  escrow.name()
                lp_token = Contract(escrow.token())
                style = "ve8020 Single Recipient"
            else:
                pool_name = gauge.name()
                lp_token = Contract(gauge.lp_token())
                style = "mainnet"
            if "getRelativeWeightCap" in gauge.selectors.values():
                cap = gauge.getRelativeWeightCap()/10**16
            else:
                cap = "N/A"
            if "getAmplificationParameter" in lp_token.selectors.values():
                (aFactor, updating, percision) = lp_token.getAmplificationParameter()
                aFactor = aFactor/percision
                if updating:
                    aFactor = f"UPDATING!! - {aFactor}"
            else:
                    aFactor  = "N/A"
            outputs.append({
                "function": command,
                "gauge_address": gauge_address,
                "type": gauge_type,
                "pool_name": pool_name,
                "lp_token": lp_token,
                "cap": f"{cap}%",
                "a_factor": aFactor,
                "style": style
            })

        return outputs


def main():
    #files = get_payload_list()
    files = ["BIPs/BIP-200-to-204.json", "BIPs/test-1.json"]
    comment = ""
    for file in files:
        file = f"../../{file}"
        results = process_file(file)
        if isinstance(results, dict):
            #  Generate Comment
            comment += (f"Gauge changes found in {file}\n```")
            comment += dicts_to_table_string(results, results[0].keys())
            comment += "\n```\n"
            #  Write Report
            p = Path(file)
            p.rename(p.with_suffix('.report.txt'))
            with open(p, "w") as report:
                report.write(dicts_to_table_string(results, results[0].keys()))
    # Handle comment
    print(comment)
    with open("output.txt", "w") as f:
        f.write(comment)


if __name__ == "__main__":
    main()