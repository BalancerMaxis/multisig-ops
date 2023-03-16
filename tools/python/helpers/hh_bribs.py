import requests
from decimal import Decimal, InvalidOperation
from web3 import Web3
import csv


SNAPSHOT_URL = "https://hub.snapshot.org/graphql?"
HH_API_URL = "https://api.hiddenhand.finance/proposal"

GAUGE_MAPPING_URL = "https://raw.githubusercontent.com/aurafinance/aura-contracts/main/tasks/snapshot/labels.json"

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
        gauge_address = Web3.toChecksumAddress(mapping["gauge"])
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
