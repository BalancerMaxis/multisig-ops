import requests
import json
import pandas as pd
import os
import re
from dotenv import load_dotenv
from helpers.addresses import get_registry_by_chain_id
from web3 import Web3
from dotmap import DotMap
# from great_ape_safe import GreatApeSafe
import collections
from helpers.addresses import get_registry_by_chain_id

INFURA_KEY = os.getenv('WEB3_INFURA_PROJECT_ID')

w3_by_chain = {
    "mainnet": Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_KEY}")),
    "arbitrum": Web3(Web3.HTTPProvider(f"https://arbitrum-mainnet.infura.io/v3/{INFURA_KEY}")),
    "optimism": Web3(Web3.HTTPProvider(f"https://optimism-mainnet.infura.io/v3/{INFURA_KEY}")),
    "polygon": Web3(Web3.HTTPProvider(f"https://polygon-mainnet.infura.io/v3/{INFURA_KEY}")),
    "gnosis": Web3(Web3.HTTPProvider(f"https://rpc.gnosischain.com/"))
}

ALL_CHAINS_MAP = {
    "mainnet": 1,
    "polygon": 137,
    "arbitrum": 42161,
    "optimism": 10,
    "gnosis": 100
}

def set_cache_durations(addresses, duration, chain="mainnet"):
    r = get_registry_by_chain_id(ALL_CHAINS_MAP[chain])
    w3 = w3_by_chain[chain]
    changelist = []
    vault = w3.eth.contract(r.balancer.vault, abi=json.load(open("./abis/IVault.json")))
    for address in addresses:
        pool = w3.eth.contract(address, abi=json.load(open("./abis/IComposibleStable.json")))
        poolId = pool.functions.getPoolId().call()
        tokens = vault.functions.getPoolTokens(poolId).call()[0]
        for token in tokens:
            if token == address:
                continue
            currentDuration = pool.functions.getTokenRateCache(token).call()[2]
            if currentDuration != duration:
                print(f"token: {token} in pool {pool.address} has a cache rate of {currentDuration} instead of {duration}")
                changelist.append([address, token])
    return(changelist)
def main():
    print(set_cache_durations([Web3.toChecksumAddress("0x50cf90b954958480b8df7958a9e965752f627124")], 5000))


if __name__ == "__main__":
    main()
