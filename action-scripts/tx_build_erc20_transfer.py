import json
import os
from web3 import Web3
import time
from bal_addresses import AddrBook

## Todo move this to bal_addresses
is_address = Web3.is_address

DRPC_KEY = os.getenv("DRPC_KEY")
W3_BY_CHAIN = {
    "base": Web3(
        Web3.HTTPProvider(f"https://lb.drpc.org/base/{DRPC_KEY}")
    ),
    "gnosis": Web3(Web3.HTTPProvider(f"https://lb.drpc.org/gnosis/{DRPC_KEY}")),
    "zkevm": Web3(Web3.HTTPProvider(f"https://lb.drpc.org/polygon-zkevm/{DRPC_KEY}")),
    "avalanche": Web3(Web3.HTTPProvider(f"https://lb.drpc.org/avalanche/{DRPC_KEY}")),
    #    "fantom": Web3(Web3.HTTPProvider(f"https://lb.drpc.org/fantom/{DRPC_KEY}")),
    ### Less reliable RPCs first to fail fast :)
    "mainnet": Web3(Web3.HTTPProvider(f"https://lb.drpc.org/ethereum/{DRPC_KEY}")),
    "arbitrum": Web3(
        Web3.HTTPProvider(f"https://lb.drpc.org/arbitrum/{DRPC_KEY}")
    ),
    "optimism": Web3(
        Web3.HTTPProvider(f"https://lb.drpc.org/optimism/{DRPC_KEY}")
    ),
    "polygon": Web3(
        Web3.HTTPProvider(f"https://lb.drpc.org/polygon/{DRPC_KEY}")
    ),
    "sepolia": Web3(Web3.HTTPProvider(f"https://lb.drpc.org/sepolia/{DRPC_KEY}")),
}

ERC20_ABI = json.load(open("abis/ERC20.json"))


def main():
    ## collect inputs
    token = os.environ["TOKEN"]
    destination = os.environ["DESTINATION"]
    amount = os.environ.get("WHOLE_AMOUNT")
    wei_amount = os.environ.get("WEI_AMOUNT")
    multisig = os.environ.get("MULTISIG")
    chain = os.environ.get("CHAIN_NAME")
    chain_id = AddrBook.chain_ids_by_name[chain.lower()]
    ## Resolve inputs
    addr_book = AddrBook(chain)
    multisig = (
        multisig if is_address(multisig) else addr_book.search_unique(multisig).address
    )
    destination = (
        destination
        if is_address(destination)
        else addr_book.search_unique(destination).address
    )

    ## get the current timestamp
    timestamp = int(time.time())
    ## assert that only one of wei_amount or whole_amount is set
    assert wei_amount != amount and (
        wei_amount or amount
    ), f"amount is {amount} and wei_amount is {wei_amount}, one and only one must bet set."
    if amount:
        # bind web3 to the token contract and get decimals()
        w3 = W3_BY_CHAIN[chain]
        token_contract = w3.eth.contract(address=token, abi=ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        # convert amount to wei
        wei_amount = int(float(amount) * 10**decimals)

    ## open the erc_20_transfer.json file in the tx_builder_templates folder
    with open("tx_builder_templates/erc20_transfer.json", "r") as f:
        tx = json.load(f)
        ## modify the tx object with the inputs
        tx["meta"]["createdFromSafeAddress"] = multisig
        tx["transactions"][0]["to"] = token
        tx["transactions"][0]["value"] = wei_amount
        tx["chainId"] = chain_id
    ## create a directory in MaxiOps/transfers for the chain if it does not exist
    if not os.path.exists(f"MaxiOps/transfers/{chain}"):
        os.makedirs(f"MaxiOps/transfers/{chain}")
    ## write a file named chain_multisig_destination_timestamp.json in the directory with the transaction json
    with open(
        f"MaxiOps/transfers/{chain}/{multisig}_{destination}_{timestamp}.json", "w"
    ) as f:
        json.dump(tx, f, indent=2)


if __name__ == "__main__":
    main()
