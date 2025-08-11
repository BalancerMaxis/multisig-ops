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

CHAIN_ADDRS = {
    "mainnet": {
        "bribe_vault": flatbook_mainnet["hidden_hand2/bribe_vault"],
        "bal_briber": flatbook_mainnet["hidden_hand2/balancer_briber"],
    },
    "arbitrum": {
        "bribe_vault": flatbook_arb["hidden_hand2/bribe_vault"],
        "bal_briber": flatbook_arb["hidden_hand2/bal_briber"],
    },
}

HH_V2_DISTRIBUTOR = "0xa9b08b4ceec1ef29edec7f9c94583270337d6416"

ABI_DIR = PROJECT_ROOT / "tools/python/abis"
paladin_distributor_abi = json.load(open(ABI_DIR / "MultiMerkleDistributorV2.json"))
erc20_abi = json.load(open(ABI_DIR / "ERC20.json"))
bribe_market_abi = json.load(open(ABI_DIR / "BribeMarket.json"))
reward_distributor_abi = json.load(open(ABI_DIR / "RewardDistributor.json"))


def fetch_claimable_paladin_bribes(address: str) -> List[dict]:
    response = requests.get(
        f"https://api.paladin.vote/quest/v3/copilot/claims/{address}"
    )
    response.raise_for_status()
    return response.json()["claims"]


def get_prop_hash(target: str) -> str:
    prop = Web3.solidity_keccak(["address"], [Web3.to_checksum_address(target)])
    return f"0x{prop.hex().lstrip('0x')}"


def create_dirs_for_date(base_path: Path, date: str):
    date_dir = base_path / date
    for chain in ["mainnet", "arbitrum"]:
        chain_dir = date_dir / chain
        os.makedirs(chain_dir, exist_ok=True)
        # with open(chain_dir / ".gitkeep", "w") as f:
        #     f.write("")
    return date_dir


def get_chain_dirs(base_dir: Path, chain_name: str) -> Path:
    return base_dir / chain_name


def claim_paladin_bribes(
    claims: List[dict], chain_name: str, date_dir: Path, builder: SafeTxBuilder
) -> str:
    """Generate tx to claim all bribes from paladin."""
    w3 = w3_by_chain[chain_name]

    unique_distributors = set(claim["distributor"] for claim in claims)
    distributor_contracts = {
        addr: SafeContract(addr, paladin_distributor_abi)
        for addr in unique_distributors
    }

    chain_dir = get_chain_dirs(date_dir, chain_name)
    csv_path = chain_dir / f"bribe_claims_{chain_name}_{CURRENT_DATE}.csv"

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
    """Format Hidden Hand claims for contract call."""
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


def fetch_hidden_hand_rewards(address: str, chain_id: int = 1) -> Dict:
    """Fetch rewards from HiddenHand API."""
    url = f"https://api.hiddenhand.finance/reward/{chain_id}/{address.lower()}"
    response = requests.get(url, timeout=10)
    if not response.ok:
        raise RuntimeError(f"Hidden Hand API returned status {response.status_code}")

    data = response.json()
    if "error" in data and data["error"]:
        raise RuntimeError(f"Hidden Hand API returned error: {data}")
    if "data" not in data:
        raise ValueError(f"Missing 'data' field in Hidden Hand API response")

    return data


def get_claimable_hidden_hand_rewards(address: str) -> List[Dict]:
    """Get claimable rewards from Hidden Hand."""
    address = Web3.to_checksum_address(address)
    claimable_rewards = []

    response = fetch_hidden_hand_rewards(address)
    rewards_data = response.get("data", [])

    for reward in rewards_data:
        protocol = reward["protocol"]
        process_reward(reward, protocol, address, claimable_rewards)

    return claimable_rewards


def process_reward(reward: dict, protocol: str, address: str, claimable_rewards: list):
    """Process a single reward."""
    claimable_amount = int(reward["cumulativeAmount"])

    if claimable_amount > 0:
        claim_data = reward["claimMetadata"]
        identifier_hex = claim_data["identifier"]
        identifier = bytes.fromhex(
            identifier_hex[2:] if identifier_hex.startswith("0x") else identifier_hex
        )

        claimable_rewards.append(
            {
                "market": protocol,
                "token": reward["token"],
                "symbol": reward.get("symbol", "UNKNOWN").upper(),
                "identifier": identifier,
                "amount": claimable_amount,
                "proof": claim_data["merkleProof"],
                "account": address,
            }
        )
        print(
            f"  - Found {reward.get('symbol', 'UNKNOWN').upper()} ({reward['token']}): {reward.get('claimable', '0')} ({claimable_amount} mantissa)"
        )


def claim_hidden_hand_bribes(
    claims: List[Dict],
    chain_name: str,
    date_dir: Path,
    builder: SafeTxBuilder,
    csv_path: str,
) -> None:
    """Generate tx to claim all bribes from Hidden Hand and append to existing CSV."""
    if chain_name != "mainnet":
        print(f"Hidden Hand claims only supported on mainnet, skipping {chain_name}")
        return

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


def deposit_paladin_bribes(csv_path: str, chain_name: str, date_dir: Path):
    """Deposit 70% of Paladin bribe amounts on HH, save 30% DAO fee."""
    chain_addrs = CHAIN_ADDRS[chain_name]
    chain_dir = get_chain_dirs(date_dir, chain_name)

    sell_csv_path = chain_dir / f"tokens_to_sell_{chain_name}_{CURRENT_DATE}.csv"

    with open(sell_csv_path, "w") as f:
        f.write("chain,token_address,amount,amount_mantissa\n")

    aggregated_bribes = {}
    hh_tokens = {}

    with open(csv_path, "r") as f:
        next(f)
        for line in f:
            parts = line.strip().split(",")
            _, bribe_market, token, gauge, _, amount_mantissa = parts

            if bribe_market == "paladin":
                key = (token, gauge)
                aggregated_bribes[key] = aggregated_bribes.get(
                    key, Decimal(0)
                ) + Decimal(amount_mantissa)
            elif bribe_market == "hiddenhand":
                # HH claims don't have gauge info, all go to sell
                hh_tokens[token] = hh_tokens.get(token, Decimal(0)) + Decimal(
                    amount_mantissa
                )

    token_sell_amounts = {}

    for (token, gauge), amount_mantissa in aggregated_bribes.items():
        print(
            f"depositing bribe on HH - token: {token}, gauge: {gauge}, amount: {amount_mantissa}"
        )

        brib_token = SafeContract(token, erc20_abi)
        briber = SafeContract(chain_addrs["bal_briber"], bribe_market_abi)

        prop_hash = get_prop_hash(gauge)
        assert prop_hash, f"no prop hash for {gauge}"

        bribe_amount_decimal = amount_mantissa * Decimal("0.7")
        bribe_amount_mantissa = int(bribe_amount_decimal)

        token_sell_amounts[token] = (
            token_sell_amounts.get(token, Decimal(0))
            + amount_mantissa
            - Decimal(bribe_amount_mantissa)
        )

        brib_token.approve(chain_addrs["bribe_vault"], bribe_amount_mantissa)
        briber.depositBribe(prop_hash, token, bribe_amount_mantissa, 0, 2)

    for token, amount_mantissa in hh_tokens.items():
        print(
            f"Adding HH claimed token to sell list - token: {token}, amount: {amount_mantissa}"
        )
        token_sell_amounts[token] = (
            token_sell_amounts.get(token, Decimal(0)) + amount_mantissa
        )

    with open(sell_csv_path, "a") as f:
        for token, sell_amount_mantissa in token_sell_amounts.items():
            token_contract = w3_by_chain[chain_name].eth.contract(
                address=Web3.to_checksum_address(token), abi=erc20_abi
            )
            decimals = token_contract.functions.decimals().call()
            amount = sell_amount_mantissa / Decimal(10**decimals)
            sell_amount_mantissa_int = int(sell_amount_mantissa)
            f.write(f"{chain_name},{token},{amount},{sell_amount_mantissa_int}\n")


if __name__ == "__main__":
    date_dir = create_dirs_for_date(BASE_PATH, CURRENT_DATE)

    claims = fetch_claimable_paladin_bribes(omni_safe)
    mainnet_claims = [claim for claim in claims if claim["chainId"] == 1]
    arb_claims = [claim for claim in claims if claim["chainId"] == 42161]

    print("\nChecking Hidden Hand rewards...")
    try:
        hh_claims = get_claimable_hidden_hand_rewards(omni_safe)
        print(f"\nFound {len(hh_claims)} Hidden Hand rewards to claim")
    except Exception as e:
        print(f"\nERROR: Failed to fetch Hidden Hand rewards: {e}")
        hh_claims = []

    for chain_name, chain_claims in [
        ("mainnet", mainnet_claims),
        ("arbitrum", arb_claims),
    ]:
        builder = SafeTxBuilder(safe_address=omni_safe, chain_name=chain_name)

        csv_path = claim_paladin_bribes(chain_claims, chain_name, date_dir, builder)

        if chain_name == "mainnet" and hh_claims:
            claim_hidden_hand_bribes(hh_claims, chain_name, date_dir, builder, csv_path)

        deposit_paladin_bribes(csv_path, chain_name, date_dir)

        builder.output_payload(
            get_chain_dirs(date_dir, chain_name)
            / f"combined_bribe_recycling_{chain_name}_{CURRENT_DATE}.json"
        )
