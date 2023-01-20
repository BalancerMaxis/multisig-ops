"""
ref: https://github.com/smartcontractkit/keeper/blob/master/contracts/UpkeepRegistrationRequests.sol
"""

import requests
import json
import pandas as pd
import os
import re
from dotenv import load_dotenv
from helpers.addresses import registry
from web3 import Web3
#from great_ape_safe import GreatApeSafe


load_dotenv()
INFURA_KEY  = os.getenv('WEB3_INFURA_PROJECT_ID')

w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_KEY}"))
w3arbitrum = Web3(Web3.HTTPProvider(f"https://arbitrum-mainnet.infura.io/v3/{INFURA_KEY}"))
w3optimism = Web3(Web3.HTTPProvider(f"https://optimism-mainnet.infura.io/v3/{INFURA_KEY}"))
w3polygon = Web3(Web3.HTTPProvider(f"https://polygon-mainnet.infura.io/v3/{INFURA_KEY}"))

authorizer=w3.eth.contract(address="0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6")

def getEvents(contract):
    i = 0
    events ={}
    for event in contract.events:
        print (i)
        gauge = Contract(controller.gauges(i))
        ## Handle Arbitrum
        if (gauge._name =="ArbitrumRootGauge"):
            crosschain_streamer = w3arbitrum.eth.contract(address=gauge.getRecipient(),
                                                          abi=json.load(open("../abi/IChildChainStreamer.json")))
            pool = crosschain_streamer.functions.reward_receiver().call()
            pool = w3arbitrum.eth.contract(address=pool, abi=json.load(open("../abi/IRewardsOnlyGauge.json")))
            gauge_name = f"ARBI: {pool.functions.name().call()}"
        elif (gauge._name =="PolygonRootGauge"):
            crosschain_streamer = w3polygon.eth.contract(address=gauge.getRecipient(),
                                                         abi=json.load(open("../abi/IChildChainStreamer.json")))
            pool = crosschain_streamer.functions.reward_receiver().call()
            pool = w3polygon.eth.contract(address=pool, abi=json.load(open("../abi/IRewardsOnlyGauge.json")))
            gauge_name = f"POLY: {pool.functions.name().call()}"
        elif (gauge._name =="OptimismRootGauge"):
            crosschain_streamer = w3optimism.eth.contract(address=gauge.getRecipient(),
                                                         abi=json.load(open("../abi/IChildChainStreamer.json")))
            pool = crosschain_streamer.functions.reward_receiver().call()
            pool = w3optimism.eth.contract(address=pool, abi=json.load(open("../abi/IRewardsOnlyGauge.json")))
            gauge_name = f"OPTI: {pool.functions.name().call()}"
        else:
            try:
                gauge_name = gauge.name()
            except Exception:
                try:
                    reward_recipient = Contract(gauge.getRecipient())
                except Exception:
                    reward_recipient = interface.IBALTokenHolder(gauge.getRecipient())
                try:
                    gauge_name = reward_recipient.name()
                except Exception:
                    gauge_name = reward_recipient.getName()
        print(f"{gauge.address}:{gauge_name}")
        if(gauge.is_killed()):
            inactive_gauges[gauge.address]=gauge_name
        else:
            active_gauges[gauge.address]=gauge_name

        i += 1

    gauges = {
        "active_gauges": active_gauges,
        "inactive_gauges": inactive_gauges
    }
    return gauges


def write_gauge_outputs(gauges_dict):
    with open('output/gauges.json', 'w') as jsonfile:
        json.dump(gauges_dict, jsonfile)
    with open('output/gauges.csv', 'w') as csvfile:
        csvfile.write("name, address, isActive\n")
        for key, value in gauges_dict["active_gauges"].items():
            csvfile.write("%s, %s, True\n" % (value, key))
        for key, value in gauges_dict["inactive_gauges"].items():
            csvfile.write(f"%s, %s, False\n" % (value, key))



def getGaugesByChain(chainId=1, printResults=False):
    ### Get chain name by ID for The Graph
    f = open("helpers/chainnames.json")
    chains_by_id = json.load(f)
    f.close()
    chain_name = chains_by_id[str(chainId)]['name']

    query = """query {
        liquidityGauges {
        symbol
        isKilled
        poolAddress
        id
        poolId
      }
    }"""
    ### Pull the subgraph data for the right chain
    if(chain_name == "mainnet"):
        url = f'https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-gauges'
    else:
        url = f'https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-gauges-{chain_name}'
    r = requests.post(url, json={'query': query})
    if (r.status_code != 200):
        print(f"Error requesting gauge list from TheGraph.  Status Code: {r.status_code}, result: {r.text}")
        exit(r.status_code)
    json_data = json.loads(r.text)

    ### Print out a resulting table
    gauge_list_json = json_data['data']['liquidityGauges']
    df = pd.DataFrame(gauge_list_json)
    df.insert(0, 'chainId', chainId)
    if (printResults):
        print(df.to_markdown(index=False))  # safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    return df


def getGaugesAllChains():
    result = {}
    ### Get chain name by ID for The Graph
    f = open("helpers/chainnames.json")
    chains_by_id = json.load(f)
    f.close()
    for (k, v) in chains_by_id.items():
        result[k] = getGaugesByChain(k)
    results = pd.concat(result, ignore_index=True)  # safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    return results;

if __name__ == '__main__':
    all_gauges_list = (getGaugesAllChains())
    print(all_gauges_list.to_markdown(index=False))
    #mainnet = getGaugesByChan(printResults=True)


