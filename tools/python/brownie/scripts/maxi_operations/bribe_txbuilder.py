import requests
from decimal import Decimal, InvalidOperation

from brownie import web3, interface, Contract
from web3 import Web3
from bal_addresses import AddrBook
import csv
from datetime import date
import json
import copy

address_book = AddrBook("mainnet")
safe = address_book.multisigs.fees
today = str(date.today())

## Hidden hands ve2 config
NO_MAX_TOKENS_PER_VOTE = 0 # No limit
PERIODS_PER_EPOCH = {
    "aura": 1,  # 1x 2 week round
    "balancer": 2  # 2x 1 week rounds
}
SNAPSHOT_URL = "https://hub.snapshot.org/graphql?"
HH_API_URL = "https://api.hiddenhand.finance/proposal"
COWSWAP_DEADLINE = 24*60*60  # 24 hours
COWSWAP_SLIPPAGE = 0.005    # 0.05%
GAUGE_MAPPING_URL = "https://raw.githubusercontent.com/aurafinance/aura-contracts/main/tasks/snapshot/gauge_choices.json"

# queries for choices and proposals info
QUERY_PROPOSAL_INFO = """
query ($proposal_id: String) {
  proposal(id: $proposal_id) {
    choices
  }
}
"""

# `state: "all"` ensures all proposals are included
QUERY_PROPOSALS = """
query {
  proposals(first: 100, where: { space: "gauges.aurafinance.eth" , state: "all"}) {
    id
  }
}
"""
with open("../tx_builder_templates/bribe_balancer.json", "r") as f:
    PAYLOAD = json.load(f)
with open("../tx_builder_templates/bribe_balancer.json", "r") as f:
    BALANCER_BRIB = json.load(f)["transactions"][0]
with open("../tx_builder_templates/bribe_aura.json", "r") as f:
    AURA_BRIB = json.load(f)["transactions"][0]
with open("../tx_builder_templates/approve.json", "r") as f:
    APPROVE = json.load(f)
with open("../tx_builder_templates/erc20_transfer.json", "r") as f:
    TRANSFER = json.load(f)


def get_hh_aura_target(target):
    response = requests.get(f"{HH_API_URL}/aura")
    options = response.json()["data"]
    for option in options:
        if Web3.toChecksumAddress(option["proposal"]) == target:
            return option["proposalHash"]
    return False  ## return false if no result

def get_gauge_name_map(map_url=GAUGE_MAPPING_URL):
    ## the url was not responding on IPv6 addresses
    requests.packages.urllib3.util.connection.HAS_IPV6 = False
    response = requests.get(map_url)
    item_list = response.json()
    output = {}
    for mapping in item_list:
        gauge_address = web3.toChecksumAddress(mapping["address"])
        output[gauge_address] = mapping["label"]
    return output

def get_index(proposal_id, target):
    # grab data from the snapshot endpoint re proposal choices
    response = requests.post(
        SNAPSHOT_URL,
        json={
            "query": QUERY_PROPOSAL_INFO,
            "variables": {"proposal_id": proposal_id},
        },
    )
    choices = response.json()["data"]["proposal"]["choices"]
    choice = choices.index(target)
    return choice

def process_bribe_csv(
       csv_file
):
    # Process the CSV
    # csv_format: target, platform, amount
    bribe_csv = list(csv.DictReader(open(csv_file)))
    aura_bribes = []
    balancer_bribes = []
    bribes = {
        "aura": {},
        "balancer": {},
        "payment": {}
    }
    ## Parse briibes per platform
    for bribe in bribe_csv:
        try:
            bribes[bribe["platform"]][bribe["target"]] = float(bribe["amount"])
        except:
           assert False, f"Error: The following brib didn't work, somethings probs wrong: \b{bribe}"
    return bribes

def main(
    csv_file=f"../../../Bribs/{today}.csv",
    usd_fee_token_address="0xfebb0bbf162e64fb9d0dfe186e517d84c395f016" ## bb-a-usd v3
):
    tx_list = []
    usdc = Contract(address_book.extras.tokens.USDC)
    usdc_mantissa_multilpier = 10 ** int(usdc.decimals())

    usdc_starting = usdc.balanceOf(safe)

    bribe_vault = address_book.extras.hidden_hand2.bribe_vault
    bribes = process_bribe_csv(csv_file)

    ### Calcualte total bribe
    total_balancer_usdc = 0
    total_aura_usdc = 0
    for target, amount in bribes["balancer"].items():
        total_balancer_usdc += amount
    for target, amount in bribes["aura"].items():
        total_aura_usdc += amount
    total_usdc = total_balancer_usdc + total_aura_usdc
    total_mantissa = int(total_usdc * usdc_mantissa_multilpier)


    usdc_approve = copy.deepcopy(APPROVE)
    usdc_approve["to"] = usdc.address
    usdc_approve["contractInputsValues"]["spender"] = bribe_vault
    usdc_approve["contractInputsValues"]["rawAmount"] = str(total_mantissa + 1)
    tx_list.append(usdc_approve)
    ### Do Payments
    payments_usd = 0
    payments = 0
    for target, amount in bribes["payment"].items():
        print(f"Paying out {amount} via direct transfer to {target}")
        print(amount)
        usdc_amount = amount * 10**usdc.decimals()
        print(usdc_amount)
        payments_usd += amount
        transfer = copy.deepcopy(TRANSFER)
        transfer["to"] = usdc.address
        transfer["contractInputsValues"]["value"] = str(int(usdc_amount))
        transfer["contractInputsValues"]["to"] = target
        tx_list.append(transfer)
        payments += usdc_amount

    ### Print report
    print(f"******** Summary Report")
    print(f"*** Aura USDC: {total_aura_usdc}")
    print(f"*** Balancer USDC: {total_balancer_usdc}")
    print(f"*** Payment USDC: {payments_usd}")
    print(f"*** Total USDC: {total_usdc + payments_usd}")
    print(f"*** Total mantissa: {int(total_mantissa + payments)}")

    ### BALANCER
    def bribe_balancer(gauge, mantissa):
        prop = web3.solidityKeccak(["address"], [Web3.toChecksumAddress(gauge)])
        mantissa = int(mantissa)

        print("******* Posting Balancer Bribe:")
        print("*** Gauge Address:", gauge)
        print("*** Proposal hash:", prop.hex())
        print("*** Amount:", amount)
        print("*** Mantissa Amount:", mantissa)

        if amount == 0:
            return
        bal_tx = copy.deepcopy(BALANCER_BRIB)
        bal_tx["contractInputsValues"]["_proposal"]=  prop.hex()
        bal_tx["contractInputsValues"]["_token"]= usdc.address
        bal_tx["contractInputsValues"]["_amount"]= str(mantissa)


        tx_list.append(bal_tx)

    for target, amount in bribes["balancer"].items():
        if amount == 0:
            continue
        mantissa = int(amount * usdc_mantissa_multilpier)
        bribe_balancer(target, mantissa)

    ### AURA
    for target, amount in bribes["aura"].items():
        if amount == 0:
            continue
        target = web3.toChecksumAddress(target)
        # grab data from proposals to find out the proposal index
        prop = get_hh_aura_target(target)
        mantissa = int(amount * usdc_mantissa_multilpier)
        # NOTE: debugging prints to verify
        print("******* Posting AURA Bribe:")
        print("*** Target Gauge Address:", target)
        print("*** Proposal hash:", prop)
        print("*** Amount:", amount)
        print("*** Mantissa Amount:", mantissa)

        if amount == 0:
            return
        tx = copy.deepcopy(AURA_BRIB)
        tx["contractInputsValues"]["_proposal"] = prop
        tx["contractInputsValues"]["_token"] = usdc.address
        tx["contractInputsValues"]["_amount"] = str(mantissa)
        tx_list.append(tx)

    usd = Contract(address_book.extras.tokens.USDC)
    bal = Contract(address_book.extras.tokens.BAL)
    print(f"Current USDC: {usd.balanceOf(safe)/ 10** usd.decimals()} is being sent to veBalFeeInjectooooooor")
    print(f"Current BAL: {bal.balanceOf(safe)/ 10** usdc.decimals()} is being sent to veBalFeeInjectooooooor")

    spent_usdc = payments + total_mantissa
    print(spent_usdc)
    usdc_trasfer = copy.deepcopy(TRANSFER)
    usdc_trasfer["to"] = usdc.address
    usdc_trasfer["contractInputsValues"]["to"] = address_book.extras.maxiKeepers.veBalFeeInjector
    usdc_trasfer["contractInputsValues"]["value"] = str(usdc.balanceOf(safe)  - spent_usdc)
    tx_list.append(usdc_trasfer)
    bal_trasfer = TRANSFER
    bal_trasfer["to"] = bal.address
    bal_trasfer["contractInputsValues"]["to"] = address_book.extras.maxiKeepers.veBalFeeInjector
    bal_trasfer["contractInputsValues"]["value"] = str(bal.balanceOf(safe))
    tx_list.append(bal_trasfer)
    print("\n\nBuilding and pushing multisig payload")
    print ("saving payload")
    payload = PAYLOAD
    payload["meta"]["createdFromSafeAddress"] = safe
    payload["transactions"] = tx_list
    with open(f"../../../BIPs/00corePools/{today}.json", "w") as f:
        json.dump(payload, f)
    print(f"balance: {usdc.balanceOf(safe)}")
    print(f"USDC to Bribs: {total_mantissa}")
    print(f"USDC payments: {payments}")
    print(f"USDC to veBAL: {usdc.balanceOf(safe)  - spent_usdc}")
    print(f"BAL to veBAL: {bal.balanceOf(safe)}")