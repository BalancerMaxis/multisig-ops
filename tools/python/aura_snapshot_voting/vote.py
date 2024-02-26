import json
import time

import requests
from bal_addresses import AddrBook
from web3 import Web3
from eth_account._utils.structured_data.hashing import hash_message, hash_domain
from eth_utils import keccak

from gen_vlaura_votes_for_epoch import gen_rev_data


flatbook = AddrBook("mainnet").flatbook

GAUGE_MAPPING_URL = "https://raw.githubusercontent.com/aurafinance/aura-contracts/main/tasks/snapshot/gauge_choices.json"
GAUGE_SNAPSHOT_URL = "https://raw.githubusercontent.com/aurafinance/aura-contracts/main/tasks/snapshot/gauge_snapshot.json"
VOTE_RELAYER_URL = "https://relayer.snapshot.org/api/msg"


def get_pool_labels(prop_choices):
    # get the mapping of eligible gauge's pools to its snapshot label
    requests.packages.urllib3.util.connection.HAS_IPV6 = False
    res = requests.get(GAUGE_MAPPING_URL)
    res.raise_for_status()
    gauge_labels = res.json()

    res = requests.get(GAUGE_SNAPSHOT_URL)
    res.raise_for_status()
    gauge_data = res.json()

    gauge_labels = {
        Web3.to_checksum_address(gauge["address"]): gauge["label"]
        for gauge in gauge_labels
    }
    gauge_pools = {
        Web3.to_checksum_address(gauge["address"]): gauge["pool"]["address"]
        for gauge in gauge_data
    }

    return {
        gauge_pools[gauge]: label
        for gauge, label in gauge_labels.items()
        if gauge in gauge_pools and label in prop_choices
    }


def hash_eip712_message(structured_data):
    domain_hash = hash_domain(structured_data)
    message_hash = hash_message(structured_data)
    return keccak(b"\x19\x01" + domain_hash + message_hash)


if __name__ == "__main__":
    df, prop = gen_rev_data()
    choices = prop["choices"]

    pool_labels = get_pool_labels(choices)

    df["snapshot_label"] = df["pool_address"].apply(
        lambda x: pool_labels.get(Web3.to_checksum_address(x))
    )
    df = df.dropna(subset=["snapshot_label"]).head(6)

    total_revenue = df["revenue"].sum()
    df["share"] = df["revenue"] / total_revenue

    vote_choices = {
        str(choices.index(row["snapshot_label"]) - 1): row["share"]
        for i, row in df.iterrows()
    }

    with open("eip712_template.json", "r") as f:
        data = json.load(f)

    data["message"]["timestamp"] = int(time.time())
    # data["from"] = flatbook["multisigs/vote_incentive_recycling"]
    data["message"]["from"] = "0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e"
    data["message"]["proposal"] = bytes.fromhex(prop["id"][2:])
    data["message"]["choice"] = str(vote_choices)

    hash = hash_eip712_message(data)

