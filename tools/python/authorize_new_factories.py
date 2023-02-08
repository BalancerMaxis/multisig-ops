import json

import requests
#from datetime import date
#from os import listdir
#from os.path import isfile, join
from helpers.addresses import get_registry_by_chain_id
import pandas as pd


debug = False

###TODO: The below settings must be set before running the script
BALANCER_DEPLOYMENTS_DIR = "../../../balancer-v2-monorepo/pkg/deployments"
BALANCER_DEPLOYMENTS_URL = "https://raw.githubusercontent.com/balancer-labs/balancer-v2-monorepo/master/pkg/deployments"
DEPLOYMENTS_LIST = [
    "20230206-weighted-pool-v3",
    "20230206-composable-stable-pool-v3"
]

### A map with the chains to handle, where key is chainid and name is the string used to identify the chain in the deployments repo path
CHAINS_MAP = {
    "mainnet": 1,
    "polygon": 137,
    "arbitrum": 42161,
}
## pause -> emergency subDAO
## disable -> emergency subDAO
## recovery mode -> emergency subDAO
## swap fee change -> fee setter contract on mainnet, treasury multisig other networks (0x7c68c42De679ffB0f16216154C996C354cF1161B), maxi safe on optimism (oeth:0x09Df1626110803C7b3b07085Ef1E053494155089)
## amp factor change -> fee setter safe on mainnet (eth:0xf4A80929163C5179Ca042E1B292F5EFBBE3D89e6), treasury multisig other networks, maxi safe on optimism

FUNCTION_CALLER_MAP = {
    "setSwapFeePercentage(uint256)": "feeManager",
    "startAmplificationParameterUpdate(uint256,uint256)": "feeManager",
    "stopAmplificationParameterUpdate()": "feeManager",
    "pause()": "emergency",
    "disable()": "emergency",
    "enableRecoveryMode()": "emergency",
}


def build_action_ids_map():
    action_ids_map = {}
    for chain_name, chain_id in CHAINS_MAP.items():
        action_ids_map[chain_name] = {}
        registry = get_registry_by_chain_id(chain_id)
        result = requests.get(f"{BALANCER_DEPLOYMENTS_URL}/action-ids/{chain_name}/action-ids.json").json()
        for deployment in DEPLOYMENTS_LIST:
            print(f"Processing {deployment}") if debug else None
            print(dict(result["deployment"])) if debug else None
            action_ids_map[chain_name][deployment] = {}
            for contract, data in result[deployment].items():
                #action_ids_map[deployment][contract]
                print(f"Processing {contract}") if debug else None
                for function, action_id in data["actionIds"].items():
                    print(f"Processing {function}") if debug else None
                    if function in FUNCTION_CALLER_MAP.keys():
#                        assert function not in action_ids_map[chain_name][deployment].keys(), f"{function} shows up in 2 contracts in {deployment}.  Stopping."
                        action_ids_map[chain_name][deployment][function] = action_id
    return action_ids_map


def generate_change_list(actions_id_map):
    changes = []
    for chain, deployments in actions_id_map.items():
        registry = get_registry_by_chain_id(CHAINS_MAP[chain])
        print(deployments)
        for deployment, functions in deployments.items():
            for function,action_id in functions.items():
                if function == "setSwapFeePercentage(uint256)" and chain == "mainnet":
                    target_address=registry.balancer.gauntletFeeSetter
                    target = "gauntletFeeSetter"
                else:
                    target_address=registry.balancer.multisigs[FUNCTION_CALLER_MAP[function]]
                    target = FUNCTION_CALLER_MAP[function]

                changes.append({
                    "deployment": deployment,
                    "chain": chain,
                    "function": function,
                    "role": action_id,
                    "target":target,
                    "target_address": target_address
                })
    return changes

def print_change_list(change_list, output_file=None):
    df = pd.DataFrame(change_list)
    print(df.to_markdown(index=False))
    if output_file:
        with open(output_file, "w") as f:
            df.to_markdown(index=False, buf=f)




def main(output_file="../../BIPs/00batched/add-v3-pools/change_list.md"):
    print_change_list(
        change_list=generate_change_list(build_action_ids_map()),
        output_file=output_file
    )

if __name__ == "__main__":
    main()