import json
import os
import time
import argparse
from functools import lru_cache
from enum import IntEnum
from pytest import approx

import requests
from bal_addresses import AddrBook
from web3 import Web3
from eth_account._utils.structured_data.hashing import hash_message, hash_domain
from eth_utils import keccak
import pandas as pd
from web3 import Web3
from gnosis.safe import Safe
from gnosis.eth import EthereumClient
from gnosis.safe.api import TransactionServiceApi
from eth_abi import encode

from gen_vlaura_votes_for_epoch import gen_rev_data


INFURA_KEY = os.getenv("WEB3_INFURA_PROJECT_ID")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

SAFE_API_URL = "https://safe-transaction-mainnet.safe.global"
GAUGE_MAPPING_URL = "https://raw.githubusercontent.com/aurafinance/aura-contracts/main/tasks/snapshot/gauge_choices.json"
GAUGE_SNAPSHOT_URL = "https://raw.githubusercontent.com/aurafinance/aura-contracts/main/tasks/snapshot/gauge_snapshot.json"
VOTE_RELAYER_URL = "https://relayer.snapshot.org/"

flatbook = AddrBook("mainnet").flatbook
vlaura_safe_addr = flatbook["multisigs/vote_incentive_recycling"]
sign_msg_lib_addr = flatbook["gnosis/sign_message_lib"]

pool_types = ["core", "sustainable", "bd"]


class Operation(IntEnum):
    CALL = 0
    DELEGATE_CALL = 1
    CREATE = 2
    

def post_safe_tx(safe_address, to_address, value, data, operation):
    ethereum_client = EthereumClient(INFURA_KEY)
    safe = Safe(safe_address, ethereum_client)
    safe_service = TransactionServiceApi(1, ethereum_client, SAFE_API_URL)

    safe_tx = safe.build_multisig_tx(to_address, value, data, operation)
    safe_tx.sign(PRIVATE_KEY)

    safe_service.post_transaction(safe_tx)


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


def get_gauge_labels(prop_choices, gauges):
    # get filtered gauge labels for manual voting
    gauge_labels = fetch_json_from_url(GAUGE_MAPPING_URL)

    gauge_labels = {
        Web3.to_checksum_address(item["address"]): item["label"]
        for item in gauge_labels
        if item["label"]
    }

    eligible_gauge_choices = {}
    gauge_addrs = [g["gauge_address"] for _type in pool_types for g in gauges[_type]["gauges"]]

    for addr in gauge_addrs:
        addr = Web3.to_checksum_address(addr)
        label = gauge_labels.get(addr)
        if label:
            if label in prop_choices:
                eligible_gauge_choices[addr] = label
            else:
                raise ValueError(f"gauge {label} not found in proposal choices")
        else:
            raise ValueError(f"gauge {addr} not found")

    return eligible_gauge_choices


def add_json_gauges(df, gauges, gauge_labels):
    for _type in pool_types:
        if gauges[_type]["allocation_pct"] > 0:
            for gauge in gauges[_type]["gauges"]:
                address = Web3.to_checksum_address(gauge["gauge_address"])
                new_row = {
                    "pool_address": address,
                    "snapshot_label": gauge_labels.get(address),
                    "vote_alloc": gauges[_type]["allocation_pct"],
                    "revenue": 0,
                    "share": gauge["weight"],
                    "blockchain": ""
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return df


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
        lambda x: pool_labels.get(Web3.to_checksum_address(x))
    )

    remaining_alloc = 1

    if args.manual:
        with open("manual_voting/manual_votes.json", "r") as f:
            manual_voting = json.load(f)
            
        gauges = {}

        base_dir = "manual_voting"
        for pool_type, pool_data in manual_voting.items():
            gauges[pool_type] = {}
            df = pd.read_csv(f"{base_dir}/{pool_data['csv_file']}")
            gauges[pool_type]["allocation_pct"] = pool_data["allocation_pct"]
            gauges[pool_type]["gauges"] = df[['gauge_address', 'weight']].to_dict(orient='records')
        
        gauge_labels = get_gauge_labels(
            choices, gauges
        )

        manual_df = df.copy()
        manual_df = add_json_gauges(manual_df, gauges, gauge_labels)
        manual_df = manual_df[manual_df["snapshot_label"].isin(gauge_labels.values())]

        remaining_alloc -= sum([gauges[t]["allocation_pct"] for t in pool_types])

    if remaining_alloc > 0:
        # distribute `remaining_alloc` evenly between top 6 core & sustainable pools
        if args.manual:
            df = df[~df["snapshot_label"].isin(manual_df["snapshot_label"].values)]
            
        df = df.dropna(subset=["snapshot_label"]).groupby("type").head(6).copy()
        
        alloc_per_type = remaining_alloc / 2

        df["vote_alloc"] = df["type"].apply(lambda x: alloc_per_type if x in ["core", "sustainable"] else 0)
        rev_per_type = df.groupby("type")["revenue"].transform("sum")
        df["share"] = (df["revenue"] / rev_per_type) * df["vote_alloc"]

    if args.manual:
        df = pd.concat([df, manual_df])

    df = df[df["share"] > 0]

    assert df["share"].sum() == approx(1, abs=0.001), f"Sum of shares is not 1: {df['share'].sum()}"

    vote_choices = {
        str(choices.index(row["snapshot_label"]) - 1): row["share"]
        for _, row in df.iterrows()
    }

    with open("eip712_template.json", "r") as f:
        data = json.load(f)

    data["message"]["timestamp"] = int(time.time())
    data["message"]["from"] = vlaura_safe_addr
    data["message"]["proposal"] = bytes.fromhex(prop["id"][2:])
    data["message"]["choice"] = str(vote_choices)

    hash = hash_eip712_message(data)

    print(f"voting for: \n{df[['blockchain', 'snapshot_label', 'share']]}")
    print(f"payload: {data}")
    print(f"hash: {hash.hex()}")

    calldata = Web3.keccak(text="signMessage(bytes)")[0:4] + encode(["bytes"], [hash])

    # post_safe_tx(vlaura_safe_addr, sign_msg_lib_addr, 0, calldata, Operation.DELEGATE_CALL)

    # prep payload for relayer
    data["types"].pop("EIP712Domain")
    data.pop("primaryType")
    data["message"]["proposal"] = prop["id"]

    response = requests.post(
        VOTE_RELAYER_URL,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Referer": "https://snapshot.org/",
        },
        data=json.dumps({"address": vlaura_safe_addr, "data": data, "sig": "0x",}),
    )

    if response.ok:
        print("Successfully posted to the vote relayer API.")
        print(response.json())
    else:
        print("Failed to post to the vote relayer API.")
        print(response.text)
        
    with open("report.txt", "w") as f:
        f.write(f"payload: {data}\n")
        f.write(f"hash: {hash.hex()}\n")

