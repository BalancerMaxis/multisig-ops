import json
from dotenv import load_dotenv
from typing import List
import sys
from pathlib import Path
import os
from datetime import datetime
from decimal import Decimal

# make parent dirs available to import from
sys.path.append(str(Path(__file__).parent.parent))

import requests
from web3 import Web3
from bal_addresses import AddrBook
from bal_tools.safe_tx_builder import SafeTxBuilder, SafeContract
from bal_tools import Web3RpcByChain
from helpers.path_utils import find_project_root


load_dotenv()


PROJECT_ROOT = find_project_root()
SCRIPT_DIR = Path(__file__).parent
BASE_PATH = PROJECT_ROOT / "MaxiOps/paladin_bribes"
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")

w3_by_chain = Web3RpcByChain(os.getenv("DRPC_KEY"))
flatbook_mainnet = AddrBook("mainnet").flatbook
flatbook_arb = AddrBook("arbitrum").flatbook

omni_safe = flatbook_mainnet["multisigs/vote_incentive_recycling"]

CHAIN_ADDRS = {
    "mainnet": {
        "paladin_distributor": flatbook_mainnet["paladin/DistributorV2"],
        "bribe_vault": flatbook_mainnet["hidden_hand2/bribe_vault"],
        "bal_briber": flatbook_mainnet["hidden_hand2/balancer_briber"],
    },
    "arbitrum": {
        "paladin_distributor": flatbook_arb["paladin/DistributorV1"],
        "bribe_vault": flatbook_arb["hidden_hand2/bribe_vault"],
        "bal_briber": flatbook_arb["hidden_hand2/bal_briber"],
    },
}

ABI_DIR = PROJECT_ROOT / "tools/python/abis"
paladin_distributor_abi = json.load(open(ABI_DIR / "MultiMerkleDistributorV2.json"))
erc20_abi = json.load(open(ABI_DIR / "ERC20.json"))
bribe_market_abi = json.load(open(ABI_DIR / "BribeMarket.json"))


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
        with open(chain_dir / ".gitkeep", "w") as f:
            f.write("")
    return date_dir


def get_chain_dirs(base_dir: Path, chain_name: str) -> Path:
    return base_dir / chain_name


def claim_paladin_bribes(claims: List[dict], chain_name: str, date_dir: Path) -> str:
    """
    - generate tx to claim all bribes from paladin
    - save claim results to csv
    """
    chain_addrs = CHAIN_ADDRS[chain_name]
    paladin_distributor = SafeContract(
        chain_addrs["paladin_distributor"], paladin_distributor_abi
    )
    w3 = w3_by_chain[chain_name]

    chain_dir = get_chain_dirs(date_dir, chain_name)
    csv_path = chain_dir / f"paladin_claims_{chain_name}_{CURRENT_DATE}.csv"

    with open(csv_path, "w") as f:
        f.write("chain,token_address,gauge_address,amount,amount_mantissa\n")

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
            amount = Decimal(claim["amount"]) / Decimal(10**decimals)

            f.write(
                f"{chain_name},{claim['token']},{claim['gauge']},{amount},{claim['amount']}\n"
            )

    return csv_path


def deposit_hh_bribes(
    csv_path: str, chain_name: str, builder: SafeTxBuilder, date_dir: Path
):
    """
    - generate tx to deposit 70% of claimed bribe amounts on HH
    - save remaining 30% (DAO fee) to separate csv
    - output final transaction payload for claims and deposits
    """
    chain_addrs = CHAIN_ADDRS[chain_name]
    chain_dir = get_chain_dirs(date_dir, chain_name)

    sell_csv_path = (
        chain_dir / f"paladin_tokens_to_sell_{chain_name}_{CURRENT_DATE}.csv"
    )

    with open(sell_csv_path, "w") as f:
        f.write("chain,token_address,amount,amount_mantissa\n")

    # Aggregate claimed bribes by amounts by token and gauge
    aggregated_bribes = {}
    with open(csv_path, "r") as f:
        next(f)
        for line in f:
            _, token, gauge, _, amount_mantissa = line.strip().split(",")
            key = (token, gauge)
            aggregated_bribes[key] = aggregated_bribes.get(key, Decimal(0)) + Decimal(
                amount_mantissa
            )

    token_sell_amounts = {}

    # Process aggregated bribes
    for (token, gauge), amount_mantissa in aggregated_bribes.items():
        print(
            f"depositing bribe on HH - token: {token}, gauge: {gauge}, amount: {amount_mantissa}"
        )

        brib_token = SafeContract(token, erc20_abi)
        briber = SafeContract(chain_addrs["bal_briber"], bribe_market_abi)

        prop_hash = get_prop_hash(gauge)
        assert prop_hash, f"no prop hash for {gauge}"

        # deposit 70%
        bribe_amount_decimal = amount_mantissa * Decimal("0.7")
        bribe_amount_mantissa = int(bribe_amount_decimal)

        # sell rest for later
        token_sell_amounts[token] = (
            token_sell_amounts.get(token, Decimal(0))
            + amount_mantissa
            - Decimal(bribe_amount_mantissa)
        )

        brib_token.approve(chain_addrs["bribe_vault"], bribe_amount_mantissa)
        briber.depositBribe(prop_hash, token, bribe_amount_mantissa, 0, 2)

    # output sell amounts to csv
    with open(sell_csv_path, "a") as f:
        for token, sell_amount_mantissa in token_sell_amounts.items():
            token_contract = w3_by_chain[chain_name].eth.contract(
                address=Web3.to_checksum_address(token), abi=erc20_abi
            )
            decimals = token_contract.functions.decimals().call()
            amount = sell_amount_mantissa / Decimal(10**decimals)
            sell_amount_mantissa_int = int(sell_amount_mantissa)
            f.write(f"{chain_name},{token},{amount},{sell_amount_mantissa_int}\n")

    builder.output_payload(
        chain_dir / f"paladin_bribe_recycling_{chain_name}_{CURRENT_DATE}.json"
    )


if __name__ == "__main__":
    date_dir = create_dirs_for_date(BASE_PATH, CURRENT_DATE)

    claims = fetch_claimable_paladin_bribes(omni_safe)
    mainnet_claims = [claim for claim in claims if claim["chainId"] == 1]
    arb_claims = [claim for claim in claims if claim["chainId"] == 42161]

    for chain_name, chain_claims in [
        ("mainnet", mainnet_claims),
        ("arbitrum", arb_claims),
    ]:
        builder = SafeTxBuilder(safe_address=omni_safe, chain_name=chain_name)
        csv_path = claim_paladin_bribes(chain_claims, chain_name, date_dir)
        deposit_hh_bribes(csv_path, chain_name, builder, date_dir)
