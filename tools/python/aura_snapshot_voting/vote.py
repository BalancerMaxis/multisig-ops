import json
import os
import time
import argparse
from functools import lru_cache
from enum import IntEnum
from pytest import approx
from dotenv import load_dotenv
from pathlib import Path
import glob
import sys

# make parent dirs available to import from
sys.path.append(str(Path(__file__).parent.parent))

import requests
from bal_addresses import AddrBook
from bal_addresses.utils import to_checksum_address
from bal_tools import Web3Rpc
from eth_account._utils.structured_data.hashing import hash_message, hash_domain
from eth_utils import keccak
import pandas as pd
from web3 import Web3
from safe_eth.safe import Safe
from safe_eth.eth import EthereumClient
from safe_eth.safe.api import TransactionServiceApi
from eth_abi import encode
from eth_account import Account

from gen_vlaura_votes_for_epoch import _get_prop_and_determine_date_range
from helpers.path_utils import find_project_root

load_dotenv()

DRPC_KEY = os.getenv("DRPC_KEY")
PRIVATE_WORDS = os.getenv("KEEPER_PRIVATE_WORDS")

SAFE_API_URL = "https://safe-transaction-mainnet.safe.global"
GAUGE_MAPPING_URL = "https://raw.githubusercontent.com/aurafinance/aura-contracts/main/tasks/snapshot/gauge_choices.json"
GAUGE_SNAPSHOT_URL = "https://raw.githubusercontent.com/aurafinance/aura-contracts/main/tasks/snapshot/gauge_snapshot.json"

LABEL_OVERRIDES = {
    "b-QuantAmmWeighted AERO/WETH/USDC/cbBTC": "b-QuantAmmWeighted AERO/USDC/cbBTC/WETH",
}

flatbook = AddrBook("mainnet").flatbook
vlaura_safe_addr = flatbook["multisigs/maxyz_operator"]
sign_msg_lib_addr = flatbook["gnosis/sign_message_lib"]

Account.enable_unaudited_hdwallet_features()


class Operation(IntEnum):
    CALL = 0
    DELEGATE_CALL = 1
    CREATE = 2


def post_safe_tx(safe_address, to_address, value, data, operation):
    api_url = Web3Rpc("mainnet", DRPC_KEY).w3.provider.endpoint_uri
    ethereum_client = EthereumClient(api_url)
    safe = Safe(safe_address, ethereum_client)
    safe_service = TransactionServiceApi(1, ethereum_client, SAFE_API_URL)

    nonce = safe_service.get_transactions(safe_address)[0]["nonce"] + 1
    safe_tx = safe.build_multisig_tx(
        to_address, value, data, operation, safe_nonce=nonce
    )

    private_key = Account.from_mnemonic(PRIVATE_WORDS).key
    safe_tx.sign(private_key.hex()[2:])

    safe_service.post_transaction(safe_tx)
    print(f"posted signMessage tx to {safe_address}")


@lru_cache(maxsize=None)
def fetch_json_from_url(url):
    # Disable IPv6 to avoid related issues
    requests.packages.urllib3.util.connection.HAS_IPV6 = False
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def hash_eip712_message(structured_data):
    domain_hash = hash_domain(structured_data)
    message_hash = hash_message(structured_data)
    return keccak(b"\x19\x01" + domain_hash + message_hash)


def format_choices(choices):
    # custom formatting so it can be properly parsed by the snapshot
    formatted_string = "{"
    for key, value in choices.items():
        formatted_string += f'"{key}":{value},'
        if key == list(choices.keys())[-1]:
            formatted_string = formatted_string[:-1]
    formatted_string += "}"
    return formatted_string


def create_voting_dirs_for_year(base_path, year, week):
    start_week = int(week[1:])
    if all(
        [
            os.path.exists(base_path / str(year) / f"W{i}")
            for i in range(start_week, 53, 2)
        ]
    ):
        return

    for i in range(start_week, 53, 2):
        voting_dir = base_path / str(year) / f"W{i}"
        input_dir = voting_dir / "input"
        output_dir = voting_dir / "output"
        os.makedirs(voting_dir, exist_ok=True)
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        with open(input_dir / ".gitkeep", "w") as f:
            f.write("")
        with open(output_dir / ".gitkeep", "w") as f:
            f.write("")


def prepare_vote_data(vote_df, prop):
    """Prepares and validates vote data, returning the structured payload"""
    choices = prop["choices"]
    gauge_labels = fetch_json_from_url(GAUGE_MAPPING_URL)
    gauge_labels = {
        to_checksum_address(x["address"]): LABEL_OVERRIDES.get(x["label"], x["label"])
        for x in gauge_labels
    }
    choice_index_map = {c: x + 1 for x, c in enumerate(choices)}

    vote_df = vote_df.dropna(subset=["Gauge Address", "Label", "Allocation %"])

    vote_df["snapshot_label"] = vote_df["Gauge Address"].apply(
        lambda x: gauge_labels.get(to_checksum_address(x.strip()))
    )
    vote_df["snapshot_index"] = vote_df["snapshot_label"].apply(
        lambda label: str(choice_index_map[label])
    )

    vote_df["share"] = vote_df["Allocation %"].str.rstrip("%").astype(float)

    assert vote_df["share"].sum() == approx(100, abs=0.0001)

    vote_choices = dict(zip(vote_df["snapshot_index"], vote_df["share"]))

    return vote_df, vote_choices


def create_vote_payload(vote_choices, prop):
    """Creates the EIP712 structured data payload"""
    project_root = find_project_root()
    template_path = project_root / "tools/python/aura_snapshot_voting"
    with open(f"{template_path}/eip712_template.json", "r") as f:
        data = json.load(f)

    data["message"]["timestamp"] = int(time.time())
    data["message"]["from"] = vlaura_safe_addr
    data["message"]["proposal"] = bytes.fromhex(prop["id"][2:])
    data["message"]["choice"] = format_choices(vote_choices)

    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vote processing script")
    parser.add_argument(
        "--week-string",
        type=str,
        help="Date that votes are are being posted. should be YYYY-W##",
    )
    year, week = parser.parse_args().week_string.split("-")

    project_root = find_project_root()
    base_path = project_root / "MaxiOps/vlaura_voting"
    voting_dir = base_path / str(year) / str(week)
    input_dir = voting_dir / "input"
    output_dir = voting_dir / "output"

    create_voting_dirs_for_year(base_path, year, week)

    vote_df = pd.read_csv(glob.glob(f"{input_dir}/*.csv")[0])

    prop, _, _ = _get_prop_and_determine_date_range()

    vote_df, vote_choices = prepare_vote_data(vote_df, prop)
    data = create_vote_payload(vote_choices, prop)
    hash = hash_eip712_message(data)

    print(f"voting for: \n{vote_df[['Chain', 'snapshot_label', 'share']]}")
    print(f"payload: {data}")
    print(f"hash: {hash.hex()}")

    calldata = Web3.keccak(text="signMessage(bytes)")[0:4] + encode(["bytes"], [hash])

    post_safe_tx(
        vlaura_safe_addr, sign_msg_lib_addr, 0, calldata, Operation.DELEGATE_CALL
    )

    data["message"]["proposal"] = prop["id"]
    data["types"].pop("EIP712Domain")
    data.pop("primaryType")

    with open(f"{output_dir}/report.txt", "w") as f:
        f.write(f"hash: 0x{hash.hex()}\n")
        f.write(f"relayer: https://relayer.snapshot.org/api/messages/0x{hash.hex()}")

    vote_df.to_csv(f"{output_dir}/vote_df.csv", index=False)

    with open(f"{output_dir}/payload.json", "w") as f:
        json.dump(data, f, indent=4)
        f.write("\n")

    response = requests.post(
        "https://relayer.snapshot.org/",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Referer": "https://snapshot.org/",
        },
        data=json.dumps(
            {
                "address": vlaura_safe_addr,
                "data": data,
                "sig": "0x",
            }
        ),
    )

    response.raise_for_status()
    print(response.text)
