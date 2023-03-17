import requests
from decimal import Decimal, InvalidOperation

from brownie import web3, interface
from web3 import Web3
from great_ape_safe import GreatApeSafe
from helpers.addresses import r
import csv
import time


SNAPSHOT_URL = "https://hub.snapshot.org/graphql?"
HH_API_URL = "https://api.hiddenhand.finance/proposal"

GAUGE_MAPPING_URL = "https://raw.githubusercontent.com/aurafinance/aura-contracts/dca03719b4bdaec29fe7f28406abf4f4d2684c37/tasks/snapshot/labels.json"

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

def get_hh_aura_target(target_name):
    response = requests.get(f"{HH_API_URL}/aura")
    options = response.json()["data"]
    for option in options:
        if option["title"] == target_name:
            return option["proposalHash"]
    return False  ## return false if no result

def get_gauge_name_map(map_url=GAUGE_MAPPING_URL):
    ## the url was not responding on IPv6 addresses
    requests.packages.urllib3.util.connection.HAS_IPV6 = False
    response = requests.get(map_url)
    item_list = response.json()
    output = {}
    for mapping in item_list:
        gauge_address = web3.toChecksumAddress(mapping["gauge"])
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
    bribe_csv = csv.DictReader(open(csv_file))
    aura_bribes = []
    balancer_bribes = []
    bribes = {
        "aura": {},
        "balancer": {}
    }
    ## Parse briibes per platform
    for bribe in bribe_csv:
        bribes[bribe["platform"]][bribe["target"]] = float(bribe["amount"])
    return bribes

def main(
    csv_file="../../../Bribs/2023-03-17.csv",
):

    safe = GreatApeSafe(r.balancer.multisigs.fees)
    #safe = GreatApeSafe("0xdc9e3Ab081B71B1a94b79c0b0ff2271135f1c12b")   # maxi playground safe

    usdc = safe.contract(r.tokens.USDC)
    usdc_mantissa_multilpier = 10 ** int(usdc.decimals())

    safe.take_snapshot([usdc])

    bribe_vault = safe.contract(r.hidden_hand.bribe_vault, interface.IBribeVault)
    aura_briber = safe.contract(r.hidden_hand.aura_briber, interface.IAuraBribe)
    balancer_briber = safe.contract(
        r.hidden_hand.balancer_briber, interface.IBalancerBribe
    )
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

    print(f"*** Aura USDC: {total_aura_usdc}")
    print(f"*** Balancer USDC: {total_balancer_usdc}")
    print(f"*** Total USDC: {total_usdc}")
    print(f"*** Total mantissa: {total_mantissa}")

    usdc.approve(bribe_vault, total_mantissa)

    ### BALANCER
    def bribe_balancer(gauge, mantissa):
        prop = web3.solidityKeccak(["address"], [Web3.toChecksumAddress(gauge)])
        mantissa = int(mantissa)

        print("*** Posting Balancer Bribe:")
        print("*** Gauge Address:", gauge)
        print("*** Proposal hash:", prop.hex())
        print("*** Amount:", amount)
        print("*** Mantissa Amount:", mantissa)
        print("\n")

        if amount == 0:
            return

        balancer_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            usdc,  # address token
            mantissa,  # uint256 amount
        )

    for target, amount in bribes["balancer"].items():
        if amount == 0:
            continue
        mantissa = int(amount * usdc_mantissa_multilpier)
        bribe_balancer(target, mantissa)

    ### AURA
    gauge_address_to_snapshot_name = get_gauge_name_map()
    for target, amount in bribes["aura"].items():
        if amount == 0:
            continue
        target_name = gauge_address_to_snapshot_name[web3.toChecksumAddress(target)]
        # grab data from proposals to find out the proposal index
        prop = get_hh_aura_target(target_name)
        mantissa = int(amount * usdc_mantissa_multilpier)
        # NOTE: debugging prints to verify
        print("*** Posting AURA Bribe:")
        print("*** Target Gauge Address:", target)
        print("*** Target Gauge name:", target_name)
        print("*** Proposal hash:", prop)
        print("*** Amount:", amount)
        print("*** Mantissa Amount:", mantissa)
        print("\n")

        if amount == 0:
            continue
        aura_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            usdc,  # address token
            mantissa,  # uint256 amount
        )

    print("\n\nBuilding and pushing multisig payload")
    print ("Preparing to post transaction")
    ### DO IT
    safe.post_safe_tx(gen_tenderly=False)

    ## The line below can be used to replace a nounce of an already loaded transaction in order to avoid having to revoke
    ## Once any tx is executed on a given nounce, all others will be canceled/impossible.
    #safe.post_safe_tx(gen_tenderly=False, replace_nonce=0)
