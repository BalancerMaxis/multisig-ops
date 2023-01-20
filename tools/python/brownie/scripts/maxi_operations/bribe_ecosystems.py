import requests
from decimal import Decimal, InvalidOperation

from brownie import web3, interface
from web3 import Web3
from great_ape_safe import GreatApeSafe
from helpers.addresses import r
import csv


SNAPSHOT_URL = "https://hub.snapshot.org/graphql?"

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
        bribes[bribe["platform"]][bribe["target"]] = bribe["amount"]
    return bribes

def main(
    csv_file="bribes/csv/current.csv",
    aura_proposal_id=None,
):

    safe = GreatApeSafe(r.balancer.multisigs.dao)
    usdc = safe.contract(r.tokens.USDC)

    safe.take_snapshot([usdc])

    bribe_vault = safe.contract(r.hidden_hand.bribe_vault, interface.IBribeVault)
    aura_briber = safe.contract(r.hidden_hand.aura_briber, interface.IAuraBribe)
    balancer_briber = safe.contract(
        r.hidden_hand.balancer_briber, interface.IBalancerBribe
    )
    bribes = process_bribe_csv(csv_file)
    ### BALANCER
    def bribe_balancer(gauge, mantissa):
        prop = web3.solidityKeccak(["address"], [Web3.toChecksumAddress(gauge)])
        mantissa = int(mantissa)

        usdc.approve(bribe_vault, mantissa)
        print(gauge, prop.hex(), mantissa)
        balancer_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            usdc,  # address token
            mantissa,  # uint256 amount
        )

    for target, amount in bribes["balancer"].items():
        mantissa = int(int(amount) * int(usdc.decimals()))
        bribe_balancer(target, mantissa)

    ### AURA
    for target, amount in bribes["aura"].items():
        assert aura_proposal_id
        choice = get_index(aura_proposal_id, target)

        # grab data from proposals to find out the proposal index
        response = requests.post(SNAPSHOT_URL, json={"query": QUERY_PROPOSALS})
        # reverse the order to have from oldest to newest
        proposals = response.json()["data"]["proposals"][::-1]
        for proposal in proposals:
            if aura_proposal_id == proposal["id"]:
                proposal_index = proposals.index(proposal)
                break
        prop = web3.solidityKeccak(["uint256", "uint256"], [proposal_index, choice])

        # NOTE: debugging prints to verify
        print("Current total proposal in aura snap: ", len(proposals))
        print("Proposal index:", proposal_index)
        print("Choice:", choice)
        print("Proposal hash:", prop.hex())
        print("Proposal amount:", amount)

        mantissa = int(int(amount) ** int(usdc.decimals()))
        usdc.approve(bribe_vault, mantissa)
        aura_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            usdc,  # address token
            mantissa,  # uint256 amount
        )

    ### DO IT
    safe.post_safe_tx()
