import json

import requests
#from datetime import date
#from os import listdir
#from os.path import isfile, join
from dotmap import DotMap
from helpers.addresses import get_registry_by_chain_id
import pandas as pd


debug = False

###TODO: The below settings must be set before running the script
BALANCER_DEPLOYMENTS_DIR = "../../../balancer-v2-monorepo/pkg/deployments"
BALANCER_DEPLOYMENTS_URL = "https://raw.githubusercontent.com/balancer-labs/balancer-v2-monorepo/master/pkg/deployments"

# List the deployments to generate permissions for
DEPLOYMENTS_LIST = [
    "20220908-weighted-pool-v2",
    "20221122-composable-stable-pool-v2"
]

### A map with the chains to handle, where key the string used to identify the chain in the deployments repo path and the value is the numeric chain id
CHAINS_MAP = {
    "gnosis": 100
}


# A map of the functions in the deployments that access should be granted to, and who should get access.
# Function should exactly match what is in the action id json and caller should exist in balancer.multisig of the address
# directory for every chain in CHAIN_MAP
FUNCTION_CALLER_MAP = {
    "disable()": "emergency",
}


def build_action_ids_map():
    action_ids_map = {}
    for chain_name, chain_id in CHAINS_MAP.items():
        action_ids_map[chain_name] = {}
        result = requests.get(f"{BALANCER_DEPLOYMENTS_URL}/action-ids/{chain_name}/action-ids.json").json()
        for deployment in DEPLOYMENTS_LIST:
            action_ids_map[chain_name][deployment] = {}
            for contract, data in result[deployment].items():
                #action_ids_map[deployment][contract]
                for function, action_id in data["actionIds"].items():
                    if function in FUNCTION_CALLER_MAP.keys():
                        action_ids_map[chain_name][deployment][function] = action_id
    return action_ids_map


def generate_change_list(actions_id_map):
    changes = []
    for chain, deployments in actions_id_map.items():
        registry = get_registry_by_chain_id(CHAINS_MAP[chain])
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

def print_change_list(change_list, outputDir=None):
    df = pd.DataFrame(change_list)
    chain_address_sorted = df.sort_values(by=["chain", "target_address"])
    chain_deployment_sorted = df.sort_values(by=["chain", "deployment", "function"])
    print(df.to_markdown(index=False))
    if outputDir:
        with open(f"{outputDir}/change_list_address_sorted.md", "w") as f:
            chain_address_sorted.to_markdown(index=False, buf=f)
        with open(f"{outputDir}/change_list_deployment_sorted.md", "w") as f:
            chain_deployment_sorted.to_markdown(index=False, buf=f)



def save_txbuilder_json(change_list, output_dir):
    df = pd.DataFrame(change_list)
    for chain_name, chain_id in CHAINS_MAP.items():
        r = get_registry_by_chain_id(chain_id)
        with open("tx_builder_templates/authorizor_grant_roles.json", "r") as f:
            data = DotMap(json.load(f))

        # Set global data
        data.chainId = chain_id
        data.meta.createFromSafeAddress = r.balancer.multisigs.dao

        # Group roles on this chain by target address
        action_ids_by_address = {}
        for change in change_list:
            if change["chain"] != chain_name:
                continue
            if change["target_address"] not in action_ids_by_address:
                action_ids_by_address[change["target_address"]] = []
            action_ids_by_address[change["target_address"]].append(change["role"])

        # Build transaction list
        transactions = []
        tx_template = data.transactions[0]
        for address,actions in action_ids_by_address.items():
            transaction = DotMap(tx_template)
            transaction.to = r.balancer.authorizer
            # TX builder wants lists in a string, addresses unquoted
            transaction.contractInputsValues.roles = str(actions).replace("'","")
            transaction.contractInputsValues.account = address
            transactions.append(dict(transaction))
        # Inject transaction list
        data.transactions = transactions
        # Save tx builder json
        with open(f"{output_dir}/add_roles_{chain_name}.json", "w") as f:
            json.dump(dict(data), f)

def main(output_dir="../../BIPs/00batched/add-v3-pools"):
    change_list = generate_change_list(build_action_ids_map())
    print_change_list(
        change_list=change_list,
        outputDir=f"{output_dir}"
    )
    save_txbuilder_json(change_list,output_dir)

if __name__ == "__main__":
    main()
