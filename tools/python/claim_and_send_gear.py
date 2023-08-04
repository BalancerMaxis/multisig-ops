import json
import requests
from dotmap import DotMap
from datetime import date
from web3 import Web3
import os
from helpers.addresses import get_registry_by_chain_id
import binascii
from helpers.hh_bribs import get_index, get_gauge_name_map, get_hh_aura_target
from bal_addresses import AddrBook

today = str(date.today())
debug = False

r = get_registry_by_chain_id(1)
a = AddrBook("mainnet")
###TODO: The below settings must be set before running the script
INFURA_KEY = os.getenv('WEB3_INFURA_PROJECT_ID')
GEARBOX_MERKLE_URL = "https://raw.githubusercontent.com/Gearbox-protocol/rewards/master/merkle/"
GEARBOX_TREE="0xA7Df60785e556d65292A2c9A077bb3A8fBF048BC"
w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_KEY}"))
tree = w3.eth.contract(address=GEARBOX_TREE, abi=json.load(open("./abis/GearAirdropDistributor.json")))


def sinlge_quote_list_string(list):
    # TX builder wants lists in a string, addresses unquoted
    output  = str(list).replace('"', "")
    return output


def claim(claim_address):
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


def main():
    ### Load Template
    with open("tx_builder_templates/base.json", "r") as f: ## framework transaction
        data = json.load(f)
    with open("tx_builder_templates/erc20_transfer.json", "r") as f:
        transfer_tx = json.load(f)

    ### Claim
    claim_tx = claim(r.balancer.multisigs.lm)
    data["transactions"].append(claim_tx)
    total_earned = claim_tx["contractInputsValues"]["totalAmount"]

    ### transfer bags to autobriboor
    already_claimed = tree.functions.claimed(r.balancer.multisigs.lm).call()
    claim_amount = int(total_earned) - int(already_claimed)
    balancer_amount = 0
    print(f"Total CLaim {int(claim_amount)/10**18} GEAR")
    transfer_tx["to"] = a.flatbook["tokens/GEAR"]
    transfer_tx["contractInputsValues"]["to"] = a.flatbook["gelatoW3f/gearboxAutoBriberV1"]
    transfer_tx["contractInputsValues"]["value"] = str(claim_amount)
    data["meta"]["createdFromSafeAddress"] = r.balancer.multisigs.lm
    data["transactions"] = [claim_tx, transfer_tx]
    with open(f"../../Bribs/partner_lm/gear/{today}.json", "w") as f: ## framework transaction
        json.dump(data, f)


if __name__ == "__main__":
    main()
