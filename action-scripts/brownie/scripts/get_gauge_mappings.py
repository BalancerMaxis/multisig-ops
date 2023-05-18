from brownie import Contract, network
from bal_addresses import AddrBook
from web3 import Web3
import json
from prettytable import PrettyTable
import os
from urllib.request import urlopen
from pathlib import Path

a = AddrBook("mainnet")
flatbook = a.flatbook
debug = False

def dicts_to_table_string(dict_list, header=None):
    table = PrettyTable(header)
    for dict_ in dict_list:
        table.add_row(list(dict_.values()))
    table.align["pool_name"] = "l"
    table.align["function"] = "l"
    table.align["style"] = "l"
    return str(table)


def get_pool_info(poolAddress):
    poolABI = json.load(open("abis/IBalPool.json", "r"))
    pool = Contract.from_abi(name="IBalPool", address=poolAddress, abi=poolABI)
    try:
        (aFactor, ramp, divisor) = pool.getAmplificationParameter()
        aFactor = int(aFactor/divisor)
        if not isinstance(aFactor, int):
            aFactor = "N/A"
    except:
        aFactor = "N/A"
    name = pool.name()
    symbol = pool.symbol()
    try:
        poolId = str(pool.getPoolId())
    except:
        poolId = "Custom"
    if pool.totalSupply ==  0:
        symbol = f"WARN: {symbol} no initjoin"
    return(name,  symbol, poolId, pool.address, aFactor)

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


def gen_report(payload_list):
    report = ""
    reports = []
    for file in payload_list:
        print(f"Processing: {file}")
        with open(f"../../{file}", "r") as json_data:
            try:
                payload = json.load(json_data)
            except:
                print(f"{file} is not proper json")
                continue
        if isinstance(payload, dict) is False:
            print(f"{file} json is not a dict")
            continue
        if "transactions" not in payload.keys():
            print(f"{file} json deos not contain a list of transactions")
            continue
        network.disconnect()
        network.connect("mainnet")
        outputs = []
        tx_list = payload["transactions"]
        gauge_controller = Contract(flatbook[a.search_unique("GaugeController")])
        for transaction in tx_list:
            style = False
            gauge_address = False
            if transaction["to"] == flatbook[a.search_unique("v3/GaugeAdder")]:
                for k in transaction["contractInputsValues"].keys():
                    if k == "rootGauge":
                        gauge_address = transaction["contractInputsValues"]["rootGauge"]
                    elif k == "gauge":
                        gauge_address = transaction["contractInputsValues"]["gauge"]
                    else:
                        print("Call to gaugeaddr without a gauge, skipping")
                        continue
                    gauge_type = "N/A"
                    command = transaction["contractMethod"]["name"]

            else:
                try:
                    if transaction["contractMethod"]["name"] != "performAction":
                        continue ## Not a passthrough tx
                except:
                    print(f"No ABI with name in payload, can't process this tx, probs not a gauge.")
                    continue
            if gauge_address == False:
                authorizer_target_contract = Web3.toChecksumAddress(transaction["contractInputsValues"]["target"])
                if authorizer_target_contract == gauge_controller:
                    try:
                        (command, inputs) = gauge_controller.decode_input(transaction["contractInputsValues"]["data"])
                    except:
                        print(f"\n\n\n ERROR: bad call data to gauge controller: {transaction['contractInputsValues']['data']}")
                        outputs.append({
                            "function": "Bad Call Data",
                            "pool_id": transaction["contractInputsValues"]["data"],
                            "symbol": "!!!",
                            "pool_address": "!!!",
                            "aFactor": "!!!",
                            "gauge_address": "!!!",
                            "type": "!!!",
                            "cap": f"!!!",
                            "style": "!!!"
                        })
                        continue
                else: # Kills are called directly on gauges, so assuming a json with gauge adds disables if it's not a gauge control it's a gauge.
                    (command, inputs) = Contract(authorizer_target_contract).decode_input(transaction["contractInputsValues"]["data"])

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
                    (pool_name, pool_symbol, poolId, pool_address, aFactor) = get_pool_info(l2hop2.lp_token())
                    style = "ChildChainStreamer"
                    gauge_symbol = l2hop2.symbol()
                else: # L0 style
                    (pool_name, pool_symbol, poolId, pool_address, aFactor) = get_pool_info(l2hop1.lp_token())
                    style = "L0 sidechain"
                    gauge_symbol = l2hop1.symbol()
                ## Go back to mainnet
                network.disconnect()
                network.connect("mainnet")
            elif "name" not in gauge.selectors.values():
                try:
                    recipient = Contract(gauge.getRecipient())
                    escrow = Contract(recipient.getVotingEscrow())
                    (pool_name, pool_symbol, poolId, pool_address, aFactor) = get_pool_info(escrow.token())
                    style = "Single Recipient"
                    gauge_symbol = "N/A"
                except:
                    style = "Single Recipient"

            else:
                (pool_name, pool_symbol, poolId, pool_address,  aFactor) = get_pool_info(gauge.lp_token())
                gauge_symbol = gauge.symbol()
                if not style:
                    style = "mainnet"
            if "getRelativeWeightCap" in gauge.selectors.values():
                cap = gauge.getRelativeWeightCap()/10**16
            else:
                cap = "N/A"

            ### Do checks
            print(f"Processed: {pool_name}, gauge: {gauge_address}, style: {style}")
            if "-gauge" in pool_symbol:
                pool_address = f"ERROR: Gauge points to another Gauge: {pool_address}"
            if pool_symbol not in gauge_symbol and "N/A" not in gauge_symbol:
                gauge_address = f"ERROR, {gauge_symbol} doesnt match {pool_symbol}: {gauge_address}"

            outputs.append({
                "function": command,
                "pool_id": str(poolId),
                "symbol": pool_symbol,
                "pool_address": pool_address,
                "aFactor": aFactor,
                "gauge_address": gauge_address,
                "type": gauge_type,
                "cap": f"{cap}%",
                "style": style
            })
        if outputs == []:
            print(f"No gauge changes found in {file}, skipping.")
            continue
        report += (f"{file}\nCOMMIT: {os.environ['COMMIT_SHA']}\n```\n")
        report += dicts_to_table_string(outputs, outputs[0].keys())
        report += "\n```\n"
        reports.append(report)
        report = ""
    return reports


def main():
    reports = gen_report(get_payload_list())
    ### Generate comment output
    with open("output.txt", "w") as f:
        for report in reports:
            f.write(report)
    ### Generate output files
    for report in reports:
        filename = Path(f"{report.splitlines()[0]}")
        filename = filename.with_suffix(".report.txt")
        with open(f"../../{filename}", "w") as f:
            f.write(report)


if __name__ == "__main__":
    main()