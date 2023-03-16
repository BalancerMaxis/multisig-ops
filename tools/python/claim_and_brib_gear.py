import json
import requests
from dotmap import DotMap
from datetime import date
from web3 import Web3
import os
from helpers.addresses import get_registry_by_chain_id
import binascii
from helpers.hh_bribs import get_index, get_gauge_name_map, get_hh_aura_target

today = str(date.today())
debug = False

r = get_registry_by_chain_id(1)

###TODO: The below settings must be set before running the script
INFURA_KEY = os.getenv('WEB3_INFURA_PROJECT_ID')
GEARBOX_MERKLE_URL = "https://raw.githubusercontent.com/Gearbox-protocol/rewards/master/merkle/"
GEARBOX_TREE="0xA7Df60785e556d65292A2c9A077bb3A8fBF048BC"
GAUGE_TO_BRIB="0x19A13793af96f534F0027b4b6a3eB699647368e7" ## bb-g-usd
w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_KEY}"))



def sinlge_quote_list_string(list):
    # TX builder wants lists in a string, addresses unquoted
    output  = str(list).replace('"', "")
    return output


def claim(claim_address, tree_address):
    tree = w3.eth.contract(address=tree_address,abi=json.load(open("./abis/GearAirdropDistributor.json")))
    b = tree.functions.merkleRoot().call()
    current_root =  binascii.hexlify(b).decode('utf-8')
    try:
        result = requests.get(f"{GEARBOX_MERKLE_URL}/mainnet_{current_root}.json")
    except requests.exceptions.HTTPError as error:
        print(result.request.url)
        print(error)
        assert(False)
    result = result.json()
    claim = result["claims"][claim_address]
    index = claim["index"]
    amount = int(claim["amount"], 0)
    proofs = claim["proof"]

    #tree.claim(index, claim_address,amount, noquote_list_string(proofs))
    with open("tx_builder_templates/gearbox_claim_tx.json", "r") as f:
        data = DotMap(json.load(f))
    tx = data.transactions[0]
    tx.contractInputsValues.index = str(index)
    tx.contractInputsValues.account = claim_address
    tx.contractInputsValues.totalAmount = str(amount)
    tx.contractInputsValues.merkleProof = str(proofs)
    return tx.toDict()


def approve(token, spender, raw_amount):
    with open("tx_builder_templates/approve.json", "r") as f:
        tx = json.load(f)
    tx["to"] = token
    tx["contractInputsValues"]["spender"] = spender
    tx["contractInputsValues"]["rawAmount"] = raw_amount
    return tx

def bribe_aura(gauge_address, bribe_token_address, amount):
    briber = w3.eth.contract(address=r.hidden_hand.aura_briber,abi=json.load(open("./abis/IAuraBriber.json")))
    target_name = get_gauge_name_map()[Web3.toChecksumAddress(gauge_address)]
    prop = get_hh_aura_target(target_name)
    with open("tx_builder_templates/bribe_aura.json", "r") as f:
        data = json.load(f)
    tx = data["transactions"][0]
    tx["contractInputsValues"]["proposal"] = prop
    tx["contractInputsValues"]["token"] = bribe_token_address
    tx["contractInputsValues"]["amount"] = str(amount)
    return tx


def main():
    ### Claim
    print(claim(r.balancer.multisigs.lm, GEARBOX_TREE))
    with open("tx_builder_templates/base.json", "r") as f: ## framework transaction
        data = json.load(f)
    claim_tx = claim(r.balancer.multisigs.lm, GEARBOX_TREE)
    data["transactions"].append(claim_tx)

    ### Bribe
    claim_amount = claim_tx["contractInputsValues"]["totalAmount"]
    print(f"Total CLaim {int(claim_amount)/10**18} GEAR")
    approve_tx = approve(r.tokens.GEAR, r.balancer.multisigs.lm, claim_amount)
    bribe_tx = bribe_aura(gauge_address=GAUGE_TO_BRIB, bribe_token_address=r.tokens.GEAR, amount=claim_amount)
    data["transactions"].append(approve_tx)
    data["transactions"].append(bribe_tx)

    data["meta"]["createdFromSafeAddress"] = r.balancer.multisigs.lm
    with open("result_payload.json", "w") as f: ## framework transaction
        json.dump(data, f)


if __name__ == "__main__":
    main()
