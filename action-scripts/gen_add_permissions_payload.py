import json
import requests
from dotmap import DotMap
from bal_addresses import AddrBook, BalPermissions, Errors
import pandas as pd
from datetime import date
from web3 import Web3
import os
from collections import defaultdict
today = str(date.today())
debug = False


script_dir = os.path.dirname(os.path.abspath(__file__))

###TODO: The below settings must be set before running the script
INFURA_KEY = os.getenv('WEB3_INFURA_PROJECT_ID')
BALANCER_DEPLOYMENTS_URL = "https://raw.githubusercontent.com/balancer/balancer-deployments/master"


W3_BY_CHAIN = {
    "mainnet": Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_KEY}")),
    "arbitrum": Web3(Web3.HTTPProvider(f"https://arbitrum-mainnet.infura.io/v3/{INFURA_KEY}")),
    "optimism": Web3(Web3.HTTPProvider(f"https://optimism-rpc.gateway.pokt.network")),
    "polygon": Web3(Web3.HTTPProvider(f"https://polygon-mainnet.infura.io/v3/{INFURA_KEY}")),
    "zkevm": Web3(Web3.HTTPProvider(f"https://zkevm-rpc.com")),
    "avalanche": Web3(Web3.HTTPProvider(f"https://avalanche-mainnet.infura.io/v3/{INFURA_KEY}")),
    "gnosis": Web3(Web3.HTTPProvider(f"https://rpc.gnosischain.com/")),
    "goerli": Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{INFURA_KEY}")),
    "sepolia": Web3(Web3.HTTPProvider(f"https://sepolia.infura.io/v3/{INFURA_KEY}")),
}

book_by_chain = {}
perms_by_chain = {}
for chain in AddrBook.chain_ids_by_name.keys():
    book_by_chain[chain] = AddrBook(chain)
    perms_by_chain[chain] = BalPermissions(chain)

def load_input_data(input_json_file):
    with open(input_json_file, "r") as f:
        data = json.load(f)
        return data

def build_action_ids_map(input_data,):
    warnings = ""
    action_ids_map = {}
    for chain_name in AddrBook.chain_ids_by_name.keys():
        action_ids_map[chain_name] = defaultdict(list)
    for change in input_data:
        for chain_name, chain_id in change["chain_map"].items():
            book = book_by_chain[chain_name]
            perms = perms_by_chain[chain_name]
            try:
                monorepo_ids = requests.get(f"{BALANCER_DEPLOYMENTS_URL}/action-ids/{chain_name}/action-ids.json")
                monorepo_ids.raise_for_status()
                monorepo_ids = monorepo_ids.json()
            except requests.HTTPError as err:
                print(f"error:{err}, url: {monorepo_ids.url}")
                exit(0)
            # TODO figure out deployment unique searching in bal addresses and use it here.
            # TODO more reporting around hit counts per chain posted to issue
            for deployment in change["deployments"]:
                for function, callers in change["function_caller_map"].items():
                    # Turn a string into a  1 item list
                    if isinstance(callers, str):
                        callers = [callers]
                    try:
                        result = perms.search_unique_path_by_unique_deployment(deployment, function)
                    except Errors.NoResultError as err:
                        warnings += f"WARNING: On chain:{chain}:{deployment}/{function}: {err}\n"

                    for caller in callers:
                        action_ids_map[chain_name][result.action_id].append(book.search_unique(caller).address)
    return action_ids_map, warnings


def generate_change_list(actions_id_map, ignore_already_set=True):
    changes = []
    warnings = ""
    for chain, action_id_infos in actions_id_map.items():
        print(chain)
        book = book_by_chain[chain]
        perms = perms_by_chain[chain]
        for action_id, callers in action_id_infos.items():
            paths = perms.paths_by_action_id[action_id]
            for path in paths:
                for caller_address in callers:
                    (deployment, contract, function) = path.split("/")
                    try:
                        authorizered_callers = perms.allowed_addresses(action_id)
                    except Errors.NoResultError:
                        authorizered_callers = []
                    if caller_address in authorizered_callers:
                        warnings += f"{deployment}/{function} already has the proper owner set, skipping.\n"
                        continue
                    caller = book.reversebook[caller_address]
                    changes.append({
                        "deployment": deployment,
                        "chain": chain,
                        "function": function,
                        "role": action_id,
                        "caller": caller,
                        "caller_address": caller_address
                    })
    return changes, warnings


def print_change_list(change_list, output_dir, filename_root=today):
    df = pd.DataFrame(change_list)
    chain_address_sorted = df.sort_values(by=["chain", "caller_address"])
    chain_deployment_sorted = df.sort_values(by=["chain", "deployment", "function"])
    print(df.to_markdown(index=False))
    if output_dir:
        with open(f"{output_dir}/{filename_root}_address_sorted.md", "w") as f:
            chain_address_sorted.to_markdown(index=False, buf=f)
        with open(f"{output_dir}/{filename_root}_deployment_sorted.md", "w") as f:
            chain_deployment_sorted.to_markdown(index=False, buf=f)

def save_command_description_table(change_list, output_dir, filename_root=today):
    referenced_calls = []
    functions=[]
    descriptions=[]
    with open(f"{output_dir}/func_desc_by_name.json", "r") as f:
        func_desc_by_name = json.load(f)
    for change in change_list:
        function = change["function"]
        if function not in referenced_calls:
            if function not in functions:
                functions.append(function)
                try:
                    descriptions.append(func_desc_by_name[function])
                except:
                    descriptions.append("description not found in map")
    df = pd.DataFrame({
        "function": functions,
        "description": descriptions
    })
    with open(f"{output_dir}/{filename_root}_function_descriptions.md", "w") as f:
        df.to_markdown(buf=f, index=False)


def save_txbuilder_json(change_list, output_dir, filename_root=today):
    df = pd.DataFrame(change_list)
    chains=[]
    for change in change_list:
        if change["chain"] not in chains:
            chains.append(change["chain"])

    for chain_name in chains:
        chain_id = AddrBook.chain_ids_by_name[chain_name]
        book = book_by_chain[chain_name]
        with open(f"{script_dir}/tx_builder_templates/authorizor_grant_roles.json", "r") as f:
            data = DotMap(json.load(f))

        # Set global data
        data.chainId = chain_id
        data.meta.createFromSafeAddress = book_by_chain[chain].search_unique("multisigs/dao").address
        # Group roles on this chain by caller address
        action_ids_by_address = {}
        for change in change_list:
            if change["chain"] != chain_name:
                continue
            if change["caller_address"] not in action_ids_by_address:
                action_ids_by_address[change["caller_address"]] = []
            action_ids_by_address[change["caller_address"]].append(change["role"])

        # Build transaction list
        transactions = []
        tx_template = data.transactions[0]
        for address,actions in action_ids_by_address.items():
            transaction = DotMap(tx_template)
            transaction.to = book.flatbook["20210418-authorizer/Authorizer"]
            # TX builder wants lists in a string, addresses unquoted
            transaction.contractInputsValues.roles = str(actions).replace("'","")
            transaction.contractInputsValues.account = address
            transactions.append(dict(transaction))
        # Inject transaction list
        data.transactions = transactions
        # Save tx builder json
        with open(f"{output_dir}/{filename_root}_{chain_name}.json", "w") as f:
            json.dump(dict(data), f, indent=2)


def main(output_dir=f"{script_dir}/../BIPs/00batched/authorizer", input_file=f"{script_dir}/../BIPs/00batched/authorizer/{today}.json"):
    input_data = load_input_data(input_file)
    (action_ids_map, warnings) = build_action_ids_map(input_data=input_data)
    print (action_ids_map)
    (change_list, w) = generate_change_list(actions_id_map=action_ids_map, ignore_already_set=True)
    warnings += "\n" + w
    print_change_list(
        change_list=change_list,
        output_dir=output_dir
    )
    save_command_description_table(change_list=change_list, output_dir=output_dir)
    save_txbuilder_json(change_list=change_list,output_dir=output_dir)
    with open(f"{output_dir}/{today}_warnings.txt", "w") as f:
        f.write(warnings)

if __name__ == "__main__":
    main()
