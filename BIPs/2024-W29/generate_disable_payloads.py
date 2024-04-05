#######
## Run this from the current directory using the requirements.txt file defined in tools/python
#######

import copy
from bal_addresses import AddrBook, BalPermissions
import json

tx_list = []
with open("disable_template.json.template", "r") as f:
    tx_tempate = json.load(f)


for chain_name in AddrBook.chain_ids_by_name.keys():
    if chain_name in ["goerli", "sepolia"]:
        continue
    print(f"Processing {chain_name}")
    a = AddrBook(chain_name)
    p = BalPermissions(chain_name)

    # Grab chain specific values from bal_addresses
    dao_multisig = a.multisigs.dao
    authorizer = a.flatbook["20210418-authorizer/Authorizer"]
    # zkEVM has a secondary deployment that needs special handling
    if chain_name == "zkevm":
        action_id =  p.search_unique_path_by_unique_deployment("20230711-zkevm-composable-stable-pool-v5", "disable()").action_id
        cspv5_factory =  a.search_unique("20230711-zkevm-composable-stable-pool-v5/ComposableStablePoolFactory").address
    else:
        action_id =  p.search_unique_path_by_unique_deployment("composable-stable-pool-v5", "disable()").action_id
        cspv5_factory =  a.search_unique("composable-stable-pool-v5/ComposableStablePoolFactory").address

    # Copy our template and get ready to work with it
    tx = copy.deepcopy(tx_tempate)
    tx["chainId"] = AddrBook.chain_ids_by_name[chain_name]
    tx["meta"]["createdFromSafeAddress"] = dao_multisig
    tx["meta"]["description"] = "Disable CSPV5 as per BIP-585"
    tx_list = tx_tempate["transactions"]

    ## Handle grant role
    grant_tx = tx_list[0]
    grant_tx["to"] = authorizer
    ## Note txbuilder requires a "stringified list"
    grant_tx["contractInputsValues"]["roles"] = "[" + action_id + "]"
    grant_tx["contractInputsValues"]["account"] = dao_multisig

    ## Handle Disable
    disable_tx = tx_list[1]
    disable_tx["to"] = cspv5_factory

    ## Handle revoke role
    grant_tx["to"] = authorizer
    grant_tx["contractInputsValues"]["role"] = action_id
    grant_tx["contractInputsValues"]["account"] = dao_multisig

    ## Dump final results
    with open (f"{chain_name}_CSP5_disable.json", "w") as f:
        json.dump(tx, f, indent=1)