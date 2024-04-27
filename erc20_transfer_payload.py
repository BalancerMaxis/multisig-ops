import json
import os
from web3 import Web3
import time

INFURA_KEY = os.getenv("INFURA_KEY")
ALCHEMY_KEY = os.getenv("ALCHEMY_KEY")

W3_BY_CHAIN = {
   "base": Web3(
        Web3.HTTPProvider(f"https://base-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}")
   ),
    "gnosis": Web3(Web3.HTTPProvider(f"https://rpc.gnosischain.com")),
    "zkevm": Web3(Web3.HTTPProvider(f"https://zkevm-rpc.com")),
    "avalanche": Web3(Web3.HTTPProvider(f"https://api.avax.network/ext/bc/C/rpc")),
    #    "fantom": Web3(Web3.HTTPProvider("https://rpc.fantom.network")),
    ### Less reliable RPCs first to fail fast :)
    "mainnet": Web3(Web3.HTTPProvider(f"https://eth-mainnet.g.alchemy.com/v2{INFURA_KEY}")),
    "arbitrum": Web3(
        Web3.HTTPProvider(f"https://arbitrum-mainnet.infura.io/v3/{INFURA_KEY}")
    ),
    "optimism": Web3(
        Web3.HTTPProvider(f"https://optimism-mainnet.infura.io/v3/{INFURA_KEY}")
    ),
    "polygon": Web3(
        Web3.HTTPProvider(f"https://polygon-mainnet.infura.io/v3/{INFURA_KEY}")
    ),
    "sepolia": Web3(Web3.HTTPProvider(f"https://sepolia.infura.io/v3/{INFURA_KEY}")),
}

ERC20_ABI = json.load(open("action-scripts/abis/ERC20.json"))

def main ():
    ## collect inputs
    token = os.environ["TOKEN"]
    destination = os.environ["DESTINATION"]
    amount = os.environ.get('WHOLE_AMOUNT')
    wei_amount = os.environ.get('WEI_AMOUNT')
    multlsig = os.environ.get('MULTISIG')
    chain = os.environ.get('CHAIN_NAME')
    ## get the current timestamp
    timestamp = int(time.time())
    ## assert that only one of wei_amount or whole_amount is set
    assert (wei_amount is None) != (amount is None), "Exactly one of wei_amount or whole_amount must be set"
    if amount:
        # bind web3 to the token contract and get decimals()
        w3 = W3_BY_CHAIN[chain]
        token_contract = w3.eth.contract(address=token, abi=ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        # convert amount to wei
        wei_amount = int(float(amount) * 10**decimals)

    ## open the erc_20_transfer.json file in the tx_builder_templates folder
    with open("action-scripts/tx_builder_templates/erc20_transfer.json", "r") as f:
        tx = json.load(f)
    ## modify the tx object with the inputs
        tx['meta']['createdFromSafeAddress'] = multlsig
        tx['transactions'][0]['to'] = token
        tx['transactions'][0]['value'] = wei_amount
        tx['chainId'] = chain
    ## create a directory in MaxiOps/transfers for the chain if it does not exist
    if not os.path.exists(f"MaxiOps/transfers/{chain}"):
        os.makedirs(f"MaxiOps/transfers/{chain}")
    ## write a file named chain_multisig_destination_timestamp.json in the directory with the transaction json
    with open(f"MaxiOps/transfers/{chain}/{multlsig}_{destination}_{timestamp}.json", "w") as f:
        json.dump(tx, f, indent=2)