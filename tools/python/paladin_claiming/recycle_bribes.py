import json
from dotenv import load_dotenv
from typing import List
import sys
from pathlib import Path
import os

sys.path.append(str(Path(__file__).parent.parent))

import requests
from web3 import Web3
from helpers.hh_bribs import get_hh_aura_target
from bal_addresses import AddrBook
from bal_tools.safe_tx_builder import SafeTxBuilder, SafeContract
from bal_tools import Web3RpcByChain


load_dotenv()

SCRIPT_DIR = Path(__file__).parent
CLAIM_OUTPUT_DIR = SCRIPT_DIR / "claim_output"
PAYLOAD_DIR = SCRIPT_DIR / "payload"

CLAIM_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)

w3_by_chain = Web3RpcByChain(os.getenv("DRPC_KEY"))
flatbook_mainnet = AddrBook("mainnet").flatbook
flatbook_arb = AddrBook("arbitrum").flatbook

omni_safe = flatbook_mainnet["multisigs/vote_incentive_recycling"]

CHAIN_ADDRS = {
    "mainnet": {
        "paladin_distributor": "0x1F7b4Bf0CD21c1FBC4F1d995BA0608fDfC992aF4",
        "bribe_vault": flatbook_mainnet["hidden_hand2/bribe_vault"],
        "bal_briber": flatbook_mainnet["hidden_hand2/balancer_briber"],
        "aura_briber": flatbook_mainnet["hidden_hand2/aura_briber"],
    },
    "arbitrum": {
        "paladin_distributor": "0xB5757D5D93a26EaA3Bc6b0b25cb2364bE8d5b90E",
        "bribe_vault": flatbook_arb["hidden_hand2/bribe_vault"],
        "bal_briber": None,  # No bal briber on arbitrum
        "aura_briber": flatbook_arb["hidden_hand2/aura_briber"],
    },
}

paladin_distributor_abi = json.load(
    open("tools/python/abis/MultiMerkleDistributorV2.json")
)
erc20_abi = json.load(open("tools/python/abis/ERC20.json"))
bribe_market_abi = json.load(open("tools/python/abis/BribeMarket.json"))


def fetch_claimable_paladin_bribes(address: str) -> List[dict]:
    response = requests.get(
        f"https://api.paladin.vote/quest/v3/copilot/claims/{address}"
    )
    response.raise_for_status()
    return response.json()["claims"]


def get_prop_hash(platform: str, target: str) -> str:
    if platform == "bal":
        prop = Web3.solidity_keccak(["address"], [Web3.to_checksum_address(target)])
        return f"0x{prop.hex().lstrip('0x')}"
    if platform == "aura":
        return get_hh_aura_target(target)
    raise ValueError(f"platform {platform} not supported")


def claim_bribes(claims: List[dict], chain_name: str) -> str:
    """
    - generate tx to claim all bribes from paladin
    - save claim results to csv
    """
    chain_addrs = CHAIN_ADDRS[chain_name]
    paladin_distributor = SafeContract(
        chain_addrs["paladin_distributor"], paladin_distributor_abi
    )
    w3 = w3_by_chain[chain_name]
    csv_path = CLAIM_OUTPUT_DIR / f"paladin_claims_{chain_name}.csv"

    with open(csv_path, "w") as f:
        f.write("chain,source,token_address,gauge_address,amount\n")

        for claim in claims:
            print(f"Claiming - token: {claim['token']}, gauge: {claim['gauge']}")

            paladin_distributor.claim(
                claim["questId"],
                claim["period"],
                claim["index"],
                claim["user"],
                claim["amount"],
                claim["proofs"],
            )

            token_contract = w3.eth.contract(
                address=Web3.to_checksum_address(claim["token"]), abi=erc20_abi
            )
            decimals = token_contract.functions.decimals().call()
            human_amount = int(claim["amount"]) / (10**decimals)

            f.write(
                f"{chain_name},{claim['path']},{claim['token']},{claim['gauge']},{human_amount}\n"
            )

    return csv_path


def deposit_bribes(csv_path: str, chain_name: str, builder: SafeTxBuilder):
    """
    process claimed bribes from csv and deposit to HH
    - generate tx to deposit 70% of claimed bribe amounts
    - save remaining 30% (DAO fee) to separate csv
    - output final transaction payload for claims and deposits
    """
    chain_addrs = CHAIN_ADDRS[chain_name]

    sell_csv_path = CLAIM_OUTPUT_DIR / f"paladin_tokens_to_sell_{chain_name}.csv"
    with open(sell_csv_path, "w") as f:
        f.write("chain,token_address,amount_wei,amount_human,decimals\n")

    bribe_data = {}
    if chain_name == "arbitrum":
        # only aura briber on arbitrum
        aura_briber = SafeContract(chain_addrs["aura_briber"], bribe_market_abi)
        bribe_data["bal"] = (aura_briber, 1)
        bribe_data["aura"] = (aura_briber, 1)
    else:
        bal_briber = SafeContract(chain_addrs["bal_briber"], bribe_market_abi)
        bribe_data["bal"] = (bal_briber, 2)

        aura_briber = SafeContract(chain_addrs["aura_briber"], bribe_market_abi)
        bribe_data["aura"] = (aura_briber, 1)

    # Aggregate claimed bribes by amounts by source, token and gauge
    aggregated_bribes = {}
    with open(csv_path, "r") as f:
        next(f)
        for line in f:
            _, source, token, gauge, amount = line.strip().split(",")
            key = (source, token, gauge)
            aggregated_bribes[key] = aggregated_bribes.get(key, 0) + float(amount)

    # Process aggregated bribes
    for (source, token, gauge), amount in aggregated_bribes.items():
        print(f"Processing bribe - token: {token}, gauge: {gauge}, amount: {amount}")

        if source not in bribe_data:
            print(
                f"source {source} not supported on {chain_name} for {token}, skipping deposit"
            )
            continue

        briber, prop_type = bribe_data[source]
        brib_token = SafeContract(token, erc20_abi)

        prop_hash = get_prop_hash(source, gauge)
        assert prop_hash, f"no prop hash for {gauge}"

        token_contract = w3_by_chain[chain_name].eth.contract(
            address=Web3.to_checksum_address(token), abi=erc20_abi
        )
        decimals = token_contract.functions.decimals().call()

        # deposit 70%
        total_amount_wei = int(amount * (10**decimals))
        bribe_amount_wei = int(total_amount_wei * 0.7)
        sell_amount_wei = total_amount_wei - bribe_amount_wei

        with open(sell_csv_path, "a") as f:
            human_amount = sell_amount_wei / (10**decimals)
            f.write(
                f"{chain_name},{token},{sell_amount_wei},{human_amount},{decimals}\n"
            )

        brib_token.approve(chain_addrs["bribe_vault"], bribe_amount_wei)
        briber.depositBribe(prop_hash, token, bribe_amount_wei, 0, prop_type)

    builder.output_payload(PAYLOAD_DIR / f"paladin_bribe_recycling_{chain_name}.json")


if __name__ == "__main__":
    claims = fetch_claimable_paladin_bribes(omni_safe)
    mainnet_claims = [claim for claim in claims if claim["chainId"] == 1]
    arb_claims = [claim for claim in claims if claim["chainId"] == 42161]

    for chain_name, chain_claims in [
        ("mainnet", mainnet_claims),
        ("arbitrum", arb_claims),
    ]:
        builder = SafeTxBuilder(safe_address=omni_safe, chain_name=chain_name)
        csv_path = claim_bribes(chain_claims, chain_name)
        deposit_bribes(csv_path, chain_name, builder)
