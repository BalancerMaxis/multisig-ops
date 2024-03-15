import json
import os
import time
import argparse
from functools import lru_cache

import requests
from bal_addresses import AddrBook
from web3 import Web3
from eth_account._utils.structured_data.hashing import hash_message, hash_domain
from eth_utils import keccak
import pandas as pd

from gen_vlaura_votes_for_epoch import gen_rev_data


CORE_ALLOC = 0.4
SUSTAINABLE_ALLOC = 0.4
BD_ALLOC = 0.2

flatbook = AddrBook("mainnet").flatbook

GAUGE_MAPPING_URL = "https://raw.githubusercontent.com/aurafinance/aura-contracts/main/tasks/snapshot/gauge_choices.json"
GAUGE_SNAPSHOT_URL = "https://raw.githubusercontent.com/aurafinance/aura-contracts/main/tasks/snapshot/gauge_snapshot.json"
VOTE_RELAYER_URL = "https://relayer.snapshot.org/api/msg"


@lru_cache(maxsize=None)
def fetch_json_from_url(url):
    # Disable IPv6 to avoid related issues
    requests.packages.urllib3.util.connection.HAS_IPV6 = False
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_pool_labels(prop_choices):
    # get the mapping of eligible gauge's pools to its snapshot label
    gauge_labels = fetch_json_from_url(GAUGE_MAPPING_URL)
    gauge_data = fetch_json_from_url(GAUGE_SNAPSHOT_URL)

    gauge_labels = {
        Web3.toChecksumAddress(gauge["address"]): gauge["label"]
        for gauge in gauge_labels
    }
    gauge_pools = {
        Web3.toChecksumAddress(gauge["address"]): gauge["pool"]["address"]
        for gauge in gauge_data
    }

    return {
        gauge_pools[gauge]: label
        for gauge, label in gauge_labels.items()
        if gauge in gauge_pools and label in prop_choices
    }


def get_gauge_labels(prop_choices, gauge_choices):
    # get filtered gauge labels for manual voting
    gauge_labels = fetch_json_from_url(GAUGE_MAPPING_URL)

    gauge_labels = {
        Web3.toChecksumAddress(item["address"]): item["label"]
        for item in gauge_labels
        if item["label"]
    }

    eligible_gauge_choices = {}

    for addr in gauge_choices:
        addr = Web3.toChecksumAddress(addr)
        label = gauge_labels.get(addr)
        if label:
            if label in prop_choices:
                eligible_gauge_choices[addr] = label
            else:
                raise ValueError(f"gauge {label} not found in proposal choices")
        else:
            raise ValueError(f"gauge {addr} not found")

    return eligible_gauge_choices


def add_gauge_to_df(df, gauge_labels, gauges, alloc_pct):
    for gauge in gauges:
        address = Web3.toChecksumAddress(gauge["address"])
        new_row = {
            "pool_address": address,
            "snapshot_label": gauge_labels.get(address),
            "vote_alloc": alloc_pct,
            "revenue": 0,
            "share": gauge["weight"]
        }
        df = pd.concat([df,  pd.DataFrame([new_row])], ignore_index=True)
    
    return df


def determine_allocation(row):
    if row["type"] == "core":
        return CORE_ALLOC
    elif row["type"] == "sustainable":
        return SUSTAINABLE_ALLOC
    else:
        return BD_ALLOC


def hash_eip712_message(structured_data):
    domain_hash = hash_domain(structured_data)
    message_hash = hash_message(structured_data)
    return keccak(b"\x19\x01" + domain_hash + message_hash)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vote processing script")
    parser.add_argument(
        "--manual", action="store_true", help="Manual vote from json file"
    )
    args = parser.parse_args()

    df, prop = gen_rev_data()
    choices = prop["choices"]

    pool_labels = get_pool_labels(choices)

    df["snapshot_label"] = df["pool_address"].apply(
        lambda x: pool_labels.get(Web3.toChecksumAddress(x))
    )

    if args.manual:
        with open("manual_voting_gauges.json", "r") as f:
            gauges = json.load(f)

        core_gauge_addresses = [g["address"] for g in gauges["core"]["gauges"]]
        sustainable_gauge_addresses = [g["address"] for g in gauges["sustainable"]["gauges"]]
        bd_gauge_addresses = [g["address"] for g in gauges["bd"]["gauges"]]

        CORE_ALLOC = gauges["core"]["allocation_pct"]
        SUSTAINABLE_ALLOC = gauges["sustainable"]["allocation_pct"]
        BD_ALLOC = gauges["bd"]["allocation_pct"]

        gauge_labels = get_gauge_labels(
            choices, core_gauge_addresses + sustainable_gauge_addresses + bd_gauge_addresses
        )

        df = add_gauge_to_df(df, gauge_labels, gauges["core"]["gauges"], CORE_ALLOC)
        df = add_gauge_to_df(df, gauge_labels, gauges["sustainable"]["gauges"], SUSTAINABLE_ALLOC)
        df = add_gauge_to_df(df, gauge_labels, gauges["bd"]["gauges"], BD_ALLOC)
        df = df[df["snapshot_label"].isin(gauge_labels.values())]

    else:
        df = df.dropna(subset=["snapshot_label"]).groupby("type").head(6).copy()

        df["vote_alloc"] = df.apply(determine_allocation, axis=1)
        rev_per_type = df.groupby("type")["revenue"].transform("sum")
        df["share"] = (df["revenue"] / rev_per_type) * df["vote_alloc"]
        df = df[df["share"] > 0]

    assert df["share"].sum() == 1

    vote_choices = {
        str(choices.index(row["snapshot_label"]) - 1): row["share"]
        for _, row in df.iterrows()
    }

    with open("eip712_template.json", "r") as f:
        data = json.load(f)

    data["message"]["timestamp"] = int(time.time())
    data["message"]["from"] = flatbook["multisigs/vote_incentive_recycling"]
    data["message"]["proposal"] = bytes.fromhex(prop["id"][2:])
    data["message"]["choice"] = str(vote_choices)

    hash = hash_eip712_message(data)

    with open("../tx_builder_templates/sign_message.json", "r") as f:
        data = json.load(f)

    data["transactions"][0]["contractInputsValues"]["_data"] = "0x" + hash.hex()

    os.makedirs("vote_txs", exist_ok=True)
    with open(f"vote_txs/vote_{hash.hex()}.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"voting for: \n{df[['blockchain', 'snapshot_label', 'share']]}")
    print(f"snapshot choice indexes: \n{vote_choices}")
    print(f"transaction saved to: \nvote_txs/vote_{hash.hex()}.json")
