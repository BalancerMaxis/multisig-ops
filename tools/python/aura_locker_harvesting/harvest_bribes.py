import json
import os
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List

import requests
from bal_addresses import AddrBook
from bal_tools import Web3RpcByChain
from bal_tools.safe_tx_builder import SafeContract, SafeTxBuilder
from dotenv import load_dotenv
from web3 import Web3

sys.path.append(str(Path(__file__).parent.parent))
from helpers.path_utils import find_project_root


load_dotenv()


PROJECT_ROOT = find_project_root()
SCRIPT_DIR = Path(__file__).parent
BASE_PATH = PROJECT_ROOT / "MaxiOps/paladin_bribes"
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")

w3_by_chain = Web3RpcByChain(os.getenv("DRPC_KEY"))
flatbook_mainnet = AddrBook("mainnet").flatbook
flatbook_arb = AddrBook("arbitrum").flatbook

omni_safe = flatbook_mainnet["multisigs/maxi_aura_locker"]

HH_V2_DISTRIBUTOR = "0xa9b08b4ceec1ef29edec7f9c94583270337d6416"

ABI_DIR = PROJECT_ROOT / "tools/python/abis"
paladin_distributor_abi = json.load(open(ABI_DIR / "MultiMerkleDistributorV2.json"))
erc20_abi = json.load(open(ABI_DIR / "ERC20.json"))
reward_distributor_abi = json.load(open(ABI_DIR / "RewardDistributor.json"))


def create_dirs_for_date(base_path: Path, date: str):
    date_dir = base_path / date
    for chain in ["mainnet", "arbitrum"]:
        chain_dir = date_dir / chain
        os.makedirs(chain_dir, exist_ok=True)
    return date_dir


def get_chain_dirs(base_dir: Path, chain_name: str) -> Path:
    return base_dir / chain_name


def claim_paladin_bribes(
    chain_name: str, chain_id: int, date_dir: Path, builder: SafeTxBuilder
) -> str:
    """Fetch and claim all bribes from paladin."""
    chain_dir = get_chain_dirs(date_dir, chain_name)
    csv_path = chain_dir / f"bribe_claims_{chain_name}_{CURRENT_DATE}.csv"
    
    # Fetch claims from Paladin API
    try:
        response = requests.get(
            f"https://api.paladin.vote/quest/v3/copilot/claims/{omni_safe}",
            timeout=30
        )
        response.raise_for_status()
        all_claims = response.json()["claims"]
    except requests.RequestException as e:
        print(f"Failed to fetch Paladin claims: {e}")
        # Create empty CSV
        with open(csv_path, "w") as f:
            f.write(
                "chain,bribe_market,token_address,gauge_address,amount,amount_mantissa\n"
            )
        return csv_path

    claims = [claim for claim in all_claims if claim["chainId"] == chain_id]

    if not claims:
        print(f"No Paladin claims found for {chain_name}")
        with open(csv_path, "w") as f:
            f.write(
                "chain,bribe_market,token_address,gauge_address,amount,amount_mantissa\n"
            )
        return csv_path

    w3 = w3_by_chain[chain_name]

    unique_distributors = set(claim["distributor"] for claim in claims)
    distributor_contracts = {
        addr: SafeContract(addr, paladin_distributor_abi)
        for addr in unique_distributors
    }

    with open(csv_path, "w") as f:
        f.write(
            "chain,bribe_market,token_address,gauge_address,amount,amount_mantissa\n"
        )

        for claim in claims:
            print(
                f"Claiming Paladin - token: {claim['token']}, gauge: {claim['gauge']}"
            )

            distributor = distributor_contracts[claim["distributor"]]
            w3_distributor = w3_by_chain[chain_name].eth.contract(
                address=Web3.to_checksum_address(claim["distributor"]),
                abi=paladin_distributor_abi,
            )

            is_claimed = w3_distributor.functions.isClaimed(
                claim["questId"], claim["period"], claim["index"]
            ).call()
            if is_claimed:
                print(f"skipping {claim['token']} because it's already claimed")
                continue

            distributor.claim(
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
            amount = Decimal(claim["amount"]) / Decimal(10**decimals)

            f.write(
                f"{chain_name},paladin,{claim['token']},{claim['gauge']},{amount},{claim['amount']}\n"
            )

    return csv_path


def format_hidden_hand_claims(claims: List[Dict]) -> List[List]:
    formatted_claims = []
    for claim in claims:
        identifier_hex = (
            claim["identifier"].hex()
            if isinstance(claim["identifier"], bytes)
            else claim["identifier"]
        )
        if not identifier_hex.startswith("0x"):
            identifier_hex = "0x" + identifier_hex

        proof_hex = []
        for p in claim["proof"]:
            if not p.startswith("0x"):
                proof_hex.append("0x" + p)
            else:
                proof_hex.append(p)

        formatted_claims.append(
            [
                identifier_hex,
                Web3.to_checksum_address(claim["account"]),
                str(claim["amount"]),
                proof_hex,
            ]
        )

    return formatted_claims


def claim_hidden_hand_bribes(
    chain_name: str,
    date_dir: Path,
    builder: SafeTxBuilder,
    csv_path: str,
) -> str:
    """Fetch and claim all bribes from Hidden Hand and append to existing CSV."""
    if chain_name != "mainnet":
        return csv_path

    print("\nChecking Hidden Hand rewards...")

    try:
        url = f"https://api.hiddenhand.finance/reward/1/{omni_safe.lower()}"
        response = requests.get(url, timeout=10)
        if not response.ok:
            print(f"Hidden Hand API returned status {response.status_code}")
            return csv_path

        data = response.json()
        if "error" in data and data["error"]:
            print(f"Hidden Hand API error: {data}")
            return csv_path

        rewards_data = data.get("data", [])
    except Exception as e:
        print(f"Failed to fetch Hidden Hand rewards: {e}")
        return csv_path

    # Process rewards into claims
    claims = []
    for reward in rewards_data:
        claimable_amount = int(reward["cumulativeAmount"])
        if claimable_amount > 0:
            claim_data = reward["claimMetadata"]
            identifier_hex = claim_data["identifier"]
            identifier = bytes.fromhex(
                identifier_hex[2:]
                if identifier_hex.startswith("0x")
                else identifier_hex
            )

            claims.append(
                {
                    "market": reward["protocol"],
                    "token": reward["token"],
                    "symbol": reward.get("symbol", "UNKNOWN").upper(),
                    "identifier": identifier,
                    "amount": claimable_amount,
                    "proof": claim_data["merkleProof"],
                    "account": omni_safe,
                }
            )
            print(
                f"  - Found {reward.get('symbol', 'UNKNOWN').upper()} ({reward['token']}): {claimable_amount} mantissa"
            )

    if not claims:
        print("No Hidden Hand rewards to claim")
        return csv_path

    print(f"\nFound {len(claims)} Hidden Hand rewards to claim")

    w3 = w3_by_chain[chain_name]
    distributor = SafeContract(HH_V2_DISTRIBUTOR, reward_distributor_abi)
    w3_distributor = w3.eth.contract(
        address=Web3.to_checksum_address(HH_V2_DISTRIBUTOR), abi=reward_distributor_abi
    )

    with open(csv_path, "a") as f:
        valid_claims = []
        for claim in claims:
            claimed_amount = w3_distributor.functions.claimed(
                claim["identifier"], Web3.to_checksum_address(claim["account"])
            ).call()

            if claimed_amount > 0:
                print(f"Skipping {claim['token']} because it's already claimed")
                continue

            print(f"Claiming HH - token: {claim['token']}, amount: {claim['amount']}")
            valid_claims.append(claim)

            token_contract = w3.eth.contract(
                address=Web3.to_checksum_address(claim["token"]), abi=erc20_abi
            )
            decimals = token_contract.functions.decimals().call()
            amount = Decimal(claim["amount"]) / Decimal(10**decimals)

            f.write(
                f"{chain_name},hiddenhand,{claim['token']},,{amount},{claim['amount']}\n"
            )

        if valid_claims:
            formatted_claims = format_hidden_hand_claims(valid_claims)
            claims_str = json.dumps(formatted_claims)
            distributor.claim(claims_str)
    
    return csv_path


def generate_tokens_to_sell_csv(csv_path: str, chain_name: str, date_dir: Path):
    """Generate CSV of all claimed tokens to be sold for AURA"""
    chain_dir = get_chain_dirs(date_dir, chain_name)
    sell_csv_path = chain_dir / f"tokens_to_sell_{chain_name}_{CURRENT_DATE}.csv"

    token_sell_amounts = {}

    with open(csv_path, "r") as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split(",")
            _, _, token, _, _, amount_mantissa = parts

            token_sell_amounts[token] = token_sell_amounts.get(
                token, Decimal(0)
            ) + Decimal(amount_mantissa)

    with open(sell_csv_path, "w") as f:
        f.write("chain,token_address,amount,amount_mantissa\n")

        for token, sell_amount_mantissa in token_sell_amounts.items():
            token_contract = w3_by_chain[chain_name].eth.contract(
                address=Web3.to_checksum_address(token), abi=erc20_abi
            )
            decimals = token_contract.functions.decimals().call()
            amount = sell_amount_mantissa / Decimal(10**decimals)
            sell_amount_mantissa_int = int(sell_amount_mantissa)

            print(f"Adding to sell list - token: {token}, amount: {amount}")
            f.write(f"{chain_name},{token},{amount},{sell_amount_mantissa_int}\n")


if __name__ == "__main__":
    date_dir = create_dirs_for_date(BASE_PATH, CURRENT_DATE)

    for chain_name, chain_id in [("mainnet", 1), ("arbitrum", 42161)]:
        builder = SafeTxBuilder(safe_address=omni_safe, chain_name=chain_name)

        csv_path = claim_paladin_bribes(chain_name, chain_id, date_dir, builder)
        claim_hidden_hand_bribes(chain_name, date_dir, builder, csv_path)
        generate_tokens_to_sell_csv(csv_path, chain_name, date_dir)

        builder.output_payload(
            get_chain_dirs(date_dir, chain_name)
            / f"bribe_claims_{chain_name}_{CURRENT_DATE}.json"
        )
