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

INFURA_KEY = os.getenv("WEB3_INFURA_PROJECT_ID")

w3_by_chain = {
    "mainnet": Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_KEY}")),
    "arbitrum": Web3(
        Web3.HTTPProvider(f"https://arbitrum-mainnet.infura.io/v3/{INFURA_KEY}")
    ),
    "optimism": Web3(
        Web3.HTTPProvider(f"https://optimism-mainnet.infura.io/v3/{INFURA_KEY}")
    ),
    "polygon": Web3(
        Web3.HTTPProvider(f"https://polygon-mainnet.infura.io/v3/{INFURA_KEY}")
    ),
    "gnosis": Web3(Web3.HTTPProvider(f"https://rpc.gnosischain.com/")),
}

ALL_CHAINS_MAP = {
    "mainnet": 1,
    "polygon": 137,
    "arbitrum": 42161,
    "optimism": 10,
    "gnosis": 100,
}


def set_cache_durations(addresses, duration, chain="mainnet"):
    r = get_registry_by_chain_id(ALL_CHAINS_MAP[chain])
    w3 = w3_by_chain[chain]
    changelist = []
    vault = w3.eth.contract(r.balancer.vault, abi=json.load(open("./abis/IVault.json")))
    for address in addresses:
        pool = w3.eth.contract(
            address, abi=json.load(open("./abis/IComposibleStable.json"))
        )
        poolId = pool.functions.getPoolId().call()
        tokens = vault.functions.getPoolTokens(poolId).call()[0]
        for token in tokens:
            if token == address:
                continue
            currentDuration = pool.functions.getTokenRateCache(token).call()[2]
            if currentDuration != duration:
                print(
                    f"token: {token} in pool {pool.address} has a cache rate of {currentDuration} instead of {duration}"
                )
                changelist.append([address, token])
    return changelist


def build_changes_tx_list(changelist, duration):
    txlist = []
    with open(f"./tx_builder_templates/setTokenRateCacheDuration.json", "r") as f:
        template = json.load(f)
    for pool, token in changelist:
        tx = template[0]
        tx["to"] = pool
        tx["contractInputsValues"]["token"] = token
        tx["contractInputsValues"]["duration"] = duration
        txlist.append(tx)
    return txlist


def get_action_id(chain, deployment, contract, call):
    action_ids_list = f"https://raw.githubusercontent.com/balancer-labs/balancer-v2-monorepo/master/pkg/deployments/action-ids/{chain}/action-ids.json"
    try:
        result = requests.get(action_ids_list).json()
    except requests.exceptions.HTTPError as err:
        print(f"URL: {requests.request.url} returned error {err}")
    return result[deployment][contract]["actionIds"][call]


def grant_permissions(actionId, chain):
    r = get_registry_by_chain_id(ALL_CHAINS_MAP[chain])
    with open(f"./tx_builder_templates/authorizor_grant_roles.json", "r") as f:
        template = json.load(f)
    tx = template["transactions"][0]
    tx["to"] = r.balancer.Authorizer
    tx["contractInputsValues"]["roles"] = [actionId]
    tx["contractInputsValues"]["account"] = r.balancer.multisigs.dao
    return tx


def revoke_permissions(actionId, chain):
    r = get_registry_by_chain_id(ALL_CHAINS_MAP[chain])
    with open(f"./tx_builder_templates/authorizor_grant_roles.json", "r") as f:
        template = json.load(f)
    tx = template["transactions"][0]
    tx["to"] = r.balancer.Authorizer
    tx["contractMethod"]["name"] = "revokeRoles"
    tx["contractInputsValues"]["roles"] = [actionId]
    tx["contractInputsValues"]["account"] = r.balancer.multisigs.dao
    return tx


def main(chain="mainnet"):
    ###  Grant Permissions
    tx_list = []
    actionId = get_action_id(
        chain=chain,
        deployment="20230206-composable-stable-pool-v3",
        contract="ComposableStablePool",
        call="setTokenRateCacheDuration(address,uint256)",
    )
    tx_list.append(grant_permissions(actionId, chain))
    ###  Make Changes
    changelist = set_cache_durations(
        [Web3.toChecksumAddress("0x50cf90b954958480b8df7958a9e965752f627124")], 21600
    )
    tx_list.extend(build_changes_tx_list(changelist, 21600))
    ###  Revoke Permissions
    tx_list.append(revoke_permissions(actionId, chain))

    with open(f"./rateChangeTxList.json", "w") as f:
        json.dump(tx_list, f)


if __name__ == "__main__":
    main()
