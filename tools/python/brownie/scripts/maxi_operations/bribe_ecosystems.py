import requests
from decimal import Decimal, InvalidOperation

from brownie import web3, interface
from web3 import Web3
from great_ape_safe import GreatApeSafe
from bal_addresses import AddrBook
import csv
from datetime import date

address_book = AddrBook("mainnet")
addr_dotmap = address_book.dotmap

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

    safe = GreatApeSafe(addr_dotmap.multisigs.fees)
    safe.init_cow(prod=True)

    usdc = safe.contract(addr_dotmap.tokens.USDC)
    usdc_mantissa_multilpier = 10 ** int(usdc.decimals())

    usdc_starting = usdc.balanceOf(safe.address)

    safe.take_snapshot([usdc])
    bribe_vault = safe.contract(addr_dotmap.hidden_hand2.bribe_vault, interface.IBribeMarket)
    aura_briber = safe.contract(addr_dotmap.hidden_hand2.aura_briber)
    balancer_briber = safe.contract(addr_dotmap.hidden_hand2.balancer_briber)
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


    usdc.approve(bribe_vault, total_mantissa + 1) #see if this fixes balance problems

    ### Do Payments
    payments_usd = 0
    payments = 0
    for target, amount in bribes["payment"].items():
        print(f"Paying out {amount} via direct transfer to {target}")
        usdc_amount = amount * 10**usdc.decimals()
        payments_usd += amount
        usdc.transfer(target, usdc_amount)
        payments += payments_usd * 10**usdc.decimals()

    ### Print report
    print(f"******** Summary Report")
    print(f"*** Aura USDC: {total_aura_usdc}")
    print(f"*** Balancer USDC: {total_balancer_usdc}")
    print(f"*** Payment USDC: {payments_usd}")
    print(f"*** Total USDC: {total_usdc + payments_usd}")
    print(f"*** Total mantissa: {int(total_mantissa + payments)}")
    print(f"*** Curent USDC mantissa: {usdc_starting}\n\n")
    print(f"Current USDC:", usdc.allowance(safe.address, bribe_vault) / usdc_mantissa_multilpier)

    ### BALANCER
    def bribe_balancer(gauge, mantissa):
        prop = web3.solidityKeccak(["address"], [Web3.toChecksumAddress(gauge)])
        mantissa = int(mantissa)

        print("******* Posting Balancer Bribe:")
        print("*** Gauge Address:", gauge)
        print("*** Proposal hash:", prop.hex())
        print("*** Amount:", amount)
        print("*** Mantissa Amount:", mantissa)
        print(f"Current USDC: {usdc.balanceOf(safe.address) / usdc_mantissa_multilpier}")

        if amount == 0:
            return

        b4brib = usdc.balanceOf(safe.address)
        balancer_briber.depositBribe(
            prop,  # bytes32 proposal
            usdc,  # address token
            mantissa,  # uint256 amount
            NO_MAX_TOKENS_PER_VOTE,  # uint256 maxTokensPerVote
            PERIODS_PER_EPOCH["balancer"]  # uint246 periods
        )
        assert b4brib - usdc.balanceOf(safe.address) == mantissa, "Unexpected tokens spent."



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
        print(f"Current USDC:", usdc.allowance(safe.address, bribe_vault) / usdc_mantissa_multilpier)

        if amount == 0:
            continue
        b4brib = usdc.balanceOf(safe.address)
        aura_briber.depositBribe(
            prop,  # bytes32 proposal
            usdc,  # address token
            mantissa,  # uint256 amount
            NO_MAX_TOKENS_PER_VOTE, # uint256 maxTokensPerVote
            PERIODS_PER_EPOCH["aura"] # uint246 periods
        )
        assert b4brib - usdc.balanceOf(safe.address) == mantissa, "Unexpected tokens spent,"

    usd = safe.contract(addr_dotmap.tokens.USDC)
    bal = safe.contract(addr_dotmap.tokens.BAL)
    print(f"Current USDC: {usd.balanceOf(safe.address)/ 10** usd.decimals()} is being sent to veBalFeeInjectooooooor")
    print(f"Current BAL: {bal.balanceOf(safe.address)/ 10** usdc.decimals()} is being sent to veBalFeeInjectooooooor")

    usdc.transfer(addr_dotmap.maxiKeepers.veBalFeeInjector, usdc.balanceOf(safe.address))
    bal.transfer(addr_dotmap.maxiKeepers.veBalFeeInjector, bal.balanceOf(safe.address))
    print("\n\nBuilding and pushing multisig payload")
    print ("Preparing to post transaction")

    ### DO IT
    safe.post_safe_tx(gen_tenderly=False)

    ## The line below can be used to replace a nounce of an already loaded transaction in order to avoid having to revoke
    ## Once any tx is executed on a given nounce, all others will be canceled/impossible.
    #safe.post_safe_tx(gen_tenderly=False, replace_nonce=0)
