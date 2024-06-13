import json
import os
from web3 import Web3
import time
from bal_addresses import AddrBook, is_address, to_checksum_address


INFURA_KEY = os.getenv("INFURA_KEY")
ALCHEMY_KEY = os.getenv("ALCHEMY_KEY")

## TODO refactor this script to use python native pathing and be less sensitive about where it is run from
GAUGE_ABI = json.load(open("action-scripts/abis/ChildChainGauge.json"))


def main():
    ## collect inputs
    token = os.environ["TOKEN"]
    distributor = os.environ["DISTRIBUTOR"]
    gauge = os.environ.get("GAUGE")
    chain = os.environ.get("CHAIN_NAME")
    chain_id = AddrBook.chain_ids_by_name[chain.lower()]
    ## Resolve inputs
    addr_book = AddrBook(chain)
    distributor = (
        distributor
        if is_address(distributor)
        else addr_book.search_unique(distributor).address
    )
    gauge = gauge if is_address(gauge) else addr_book.search_unique(gauge).address
    # Set data equal to add_rewards(token, distributor) calldata encoded
    w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
    gauge_interface = w3.eth.contract(address=to_checksum_address(gauge), abi=GAUGE_ABI)
    data = gauge_interface.encodeABI(fn_name="add_reward", args=[token, distributor])
    # open the add_reward_token_to_gauge.json file and modify it with the object inputs
    with open("action-scripts/tx_builder_templates/add_reward_token.json", "r") as f:
        tx = json.load(f)
        tx["chainId"] = chain_id
        tx["meta"]["createdFromSafeAddress"] = addr_book.multisigs.lm
        tx["transactions"][0]["to"] = addr_book.search_unique(
            "AuthorizerAdaptorEntrypoint"
        )
        tx["transactions"][0]["contractInputsValues"]["data"] = str(data)
        tx["transactions"][0]["contractInputsValues"]["target"] = gauge
    ## create a directory in MaxiOps/transfers for the chain if it does not exist
    if not os.path.exists(f"MaxiOps/add_rewards/{chain}"):
        os.makedirs(f"MaxiOps/add_rewards/{chain}")
    ## write a file named chain_multisig_destination_timestamp.json in the directory with the transaction json
    timestamp = int(time.time())
    with open(
        f"MaxiOps/add_rewards/{chain}/{gauge}_{token}_{timestamp}.json", "w"
    ) as f:
        json.dump(tx, f, indent=2)


if __name__ == "__main__":
    main()
