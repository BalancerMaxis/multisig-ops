import json
import os
import pickle
import requests
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from pytest import approx

import numpy as np
import pandas as pd
from requests import Session
from requests.adapters import HTTPAdapter, Retry
from web3 import Web3, exceptions

from bal_addresses.addresses import ZERO_ADDRESS, to_checksum_address
from bal_tools import Subgraph, BalPoolsGauges


WATCHLIST = json.load(open("tools/python/gen_merkl_airdrops_watchlist.json"))
BALANCER_VAULT_V3 = "0xbA1333333333a1BA1108E8412f11850A5C319bA9"
OMNI_MSIG = "0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e"  # Omni multisig address for Merit campaigns
AURA_VOTER_PROXY = "0xaF52695E1bB01A16D33D7194C28C42b10e0Dbec2"
AURA_VOTER_PROXY_LITE = "0xC181Edc719480bd089b94647c2Dc504e2700a2B0"
BEEFY_PARTNER_BASE_URL = (
    "https://balance-api.beefy.finance/api/v1/partner/balancer/config"
)
AAVECHAN_MERIT_API = (
    f"https://apps.aavechan.com/api/merit/rewards?user={OMNI_MSIG.lower()}"
)
CHAINS = {"1": "MAINNET", "8453": "BASE", "43114": "AVALANCHE"}
CHAIN_SLUGS = {"1": "ethereum", "8453": "base", "43114": "avalanche"}
ADAPTER = HTTPAdapter(
    pool_connections=20,
    pool_maxsize=20,
    max_retries=Retry(
        total=10, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504, 520]
    ),
)


def get_user_shares_pool(pool, block):
    raw = subgraph.fetch_graphql_data(
        "vault-v3",
        "get_user_shares_by_pool",
        {"pool": pool.lower(), "block": block},
    )
    return dict([(x["user"]["id"], Decimal(x["balance"])) for x in raw["poolShares"]])


def get_user_shares_gauge(gauge, block):
    raw = subgraph.fetch_graphql_data(
        "gauges",
        "fetch_gauge_shares",
        {"gaugeAddress": gauge, "block": block},
    )
    return (
        dict([(x["user"]["id"], Decimal(x["balance"])) for x in raw["gaugeShares"]])
        if gauge
        else {}
    )


def get_user_shares_aura(pool, block):
    raw = subgraph.fetch_graphql_data(
        "aura",
        "get_aura_user_pool_balances_by_lp",
        {"lpToken": pool.lower(), "block": block},
    )
    return (
        dict(
            [
                (x["account"]["id"], Decimal(x["staked"]) / Decimal(1e18))
                for x in raw["pools"][0]["accounts"]
            ]
        )
        if raw.get("pools")
        else {}
    )


def get_user_shares_beefy(pool, block):
    beefy_slug = "avax" if chain == "43114" else CHAIN_SLUGS[chain]
    r = session_beefy.get(BEEFY_PARTNER_BASE_URL + f"/{beefy_slug}/{block}/bundles")
    r.raise_for_status()
    raw_beefy = r.json()
    for vault in raw_beefy:
        if vault["vault_config"]["undelying_lp_address"].lower() == pool.lower():
            return dict(
                [
                    (x["holder"], Decimal(x["balance"]) / Decimal(1e18))
                    for x in vault["holders"]
                ]
            )
    return {}


def get_beefy_strat(pool, block):
    beefy_slug = "avax" if chain == "43114" else CHAIN_SLUGS[chain]
    r = session_beefy.get(BEEFY_PARTNER_BASE_URL + f"/{beefy_slug}/{block}/bundles")
    r.raise_for_status()
    raw_beefy = r.json()
    for vault in raw_beefy:
        if vault["vault_config"]["undelying_lp_address"].lower() == pool.lower():
            return vault["vault_config"]["strategy_address"]
    return ""


# Cache for timestamp to block lookups
_timestamp_block_cache = {}
_timestamp_cache_file = "MaxiOps/merkl/cache/timestamp_blocks.pkl"

# Load cache from file if it exists
if Path(_timestamp_cache_file).is_file():
    with open(_timestamp_cache_file, "rb") as f:
        _timestamp_block_cache = pickle.load(f)


def get_block_from_timestamp(ts, chain_id=None):
    # Use global chain if chain_id not provided
    chain_to_use = chain_id if chain_id is not None else chain

    # Check cache first
    cache_key = f"{chain_to_use}:{ts}"
    if cache_key in _timestamp_block_cache:
        return _timestamp_block_cache[cache_key]

    # Try subgraph first with retries for intermittent failures
    max_retries = 3
    for attempt in range(max_retries):
        try:
            raw = subgraph.fetch_graphql_data(
                "blocks",
                "first_block_after_ts",
                {"timestamp_lt": ts + step_size, "timestamp_gt": ts - 1},
            )
            block_number = int(raw["blocks"][0]["number"])
            _timestamp_block_cache[cache_key] = block_number
            # Save cache to file
            os.makedirs(os.path.dirname(_timestamp_cache_file), exist_ok=True)
            with open(_timestamp_cache_file, "wb") as f:
                pickle.dump(_timestamp_block_cache, f)
            return block_number
        except Exception as e:
            if "bad indexers" in str(e) and attempt < max_retries - 1:
                # Known intermittent issue with Base blocks subgraph
                import time

                time.sleep(1)  # Wait before retry
                continue
            # If all retries failed, fall back to Etherscan API v2
            break

    # Fallback to Etherscan API v2 (omnichain)
    import os
    import requests

    api_key = os.getenv("ETHERSCAN_API_KEY")
    if not api_key:
        raise ValueError("ETHERSCAN_API_KEY not set, cannot use fallback")

    # Etherscan v2 API endpoint
    api_url = "https://api.etherscan.io/v2/api"

    # Use the omnichain endpoint for getting block by timestamp
    params = {
        "chainid": chain_to_use,  # Chain ID (1 for mainnet, 8453 for Base, etc.)
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": ts,
        "closest": "after",
        "apikey": api_key,
    }

    response = requests.get(api_url, params=params)
    response.raise_for_status()
    data = response.json()

    if data.get("status") == "1" and data.get("result"):
        # The result is just the block number as a string
        block_number = int(data["result"])
        _timestamp_block_cache[cache_key] = block_number
        # Save cache to file
        os.makedirs(os.path.dirname(_timestamp_cache_file), exist_ok=True)
        with open(_timestamp_cache_file, "wb") as f:
            pickle.dump(_timestamp_block_cache, f)
        return block_number
    else:
        raise Exception(f"Etherscan API error: {data.get('message', 'Unknown error')}")


def build_snapshot_df(
    pool,  # pool address
    end,  # timestamp of the last snapshot
    step_size,  # amount of seconds between snapshots
):
    gauge = BalPoolsGauges(CHAINS[chain]).get_preferential_gauge(pool)
    if gauge:
        gauge = gauge.lower()
    beefy_strat = get_beefy_strat(pool, get_block_from_timestamp(end)).lower()

    # get user shares for pool and gauge at different timestamps
    pool_shares = {}
    gauge_shares = {}
    aura_shares = {}
    beefy_shares = {}
    start = end - epoch_duration
    n_snapshots = int(np.floor(epoch_duration / step_size))
    n = 1
    while end > start:
        block = get_block_from_timestamp(end)
        print(f"{n}\t/\t{n_snapshots}\t{block}")
        pool_shares[block] = get_user_shares_pool(pool=pool, block=block)
        if gauge:
            gauge_shares[block] = get_user_shares_gauge(gauge=gauge, block=block)
        else:
            gauge_shares[block] = {}
        aura_shares[block] = get_user_shares_aura(pool=pool, block=block)
        beefy_shares[block] = get_user_shares_beefy(pool=pool, block=block)
        end -= step_size
        n += 1

    contract = drpc.eth.contract(
        address=Web3.to_checksum_address(pool),
        abi=json.load(open("tools/python/abis/StablePoolV3.json")),
    )
    # calculate total shares per user per block
    total_shares = {}
    total_supply = {}
    protocol_reserves = {}
    for block in pool_shares:
        total_shares[block] = {}
        protocol_reserves[block] = Decimal(0)
        for user_id in pool_shares[block]:
            if user_id in [
                gauge,
                AURA_VOTER_PROXY.lower(),
                AURA_VOTER_PROXY_LITE.lower(),
                beefy_strat,
            ]:
                # we do not want to count the gauge or the aura voter proxy as a user;
                # these are accounted for later
                continue
            total_shares[block][user_id] = pool_shares[block][user_id]
        for user_id in gauge_shares[block]:
            if user_id in [
                AURA_VOTER_PROXY.lower(),
                AURA_VOTER_PROXY_LITE.lower(),
                beefy_strat,
            ]:
                # we do not want to count the aura voter proxy as a user;
                # it is accounted for later
                # for beefy: track the difference between what it holds and what it distributes
                # (its gauge balance != its total user shares)
                if user_id == beefy_strat and beefy_strat:
                    beefy_gauge_balance = gauge_shares[block].get(
                        beefy_strat, Decimal(0)
                    )
                    beefy_user_total = sum(beefy_shares[block].values())
                    protocol_reserves[block] += beefy_gauge_balance - beefy_user_total
                continue
            if user_id not in total_shares[block]:
                total_shares[block][user_id] = gauge_shares[block][user_id]
            else:
                total_shares[block][user_id] += gauge_shares[block][user_id]
        for user_id in aura_shares[block]:
            if user_id in [beefy_strat]:
                # we do not want to count the beefy vault as a user;
                # it is accounted for later
                continue
            if user_id not in total_shares[block]:
                total_shares[block][user_id] = aura_shares[block][user_id]
            else:
                total_shares[block][user_id] += aura_shares[block][user_id]
        for user_id in beefy_shares[block]:
            if user_id not in total_shares[block]:
                total_shares[block][user_id] = beefy_shares[block][user_id]
            else:
                total_shares[block][user_id] += beefy_shares[block][user_id]
        # collect onchain total supply per block
        # we are spamming the rpc here; needs additional retries sometimes
        retries = 5
        for i in range(retries):
            try:
                total_supply[block] = Decimal(
                    contract.functions.totalSupply().call(block_identifier=block)
                )
                break
            except exceptions.BadFunctionCallOutput as e:
                if (
                    "Could not decode contract function call to totalSupply with return data: b''"
                    in str(e)
                ):
                    # contract is not deployed yet
                    total_supply[block] = Decimal(0)
                    break
                if i < retries - 1:
                    continue
                else:
                    raise

    # build dataframe
    df = pd.DataFrame(total_shares).fillna(Decimal(0))

    # account for protocol reserves (eg beefy) that should not be distributed
    total_protocol_reserves = sum(protocol_reserves.values())
    expected_user_shares = (
        sum(total_supply.values()) / Decimal(1e18) - total_protocol_reserves
    )

    # checksum total balances versus total supply
    tolerance = Decimal(1e-2)  # 1% tolerance for all pools

    actual_total = df.sum().sum()
    discrepancy_pct = (
        abs(actual_total - expected_user_shares) / expected_user_shares
        if expected_user_shares > 0
        else 0
    )

    assert actual_total == approx(
        expected_user_shares, rel=tolerance
    ), f"total shares do not match expected user shares: {actual_total} != {expected_user_shares} (discrepancy: {discrepancy_pct:.4%}, protocol reserves: {total_protocol_reserves})"
    for block in df.columns:
        expected_block_shares = (
            total_supply[block] / Decimal(1e18) - protocol_reserves[block]
        )
        assert df[block].sum() == approx(
            expected_block_shares, rel=tolerance
        ), f"shares for block {block} do not match expected: {df[block].sum()} != {expected_block_shares} (protocol reserves: {protocol_reserves[block]})"

    return df


def determine_morpho_breakdown(pools, end, step_size):
    end_cached = end
    morpho_values = {}
    for pool in pools:
        instance = f"{epoch_name}-{step_size}-{protocol}-{chain}-{pool}".replace(
            "/", "_"
        )
        cache_dir = "MaxiOps/merkl/cache/morpho_usd/"
        os.makedirs(os.path.dirname(cache_dir), exist_ok=True)
        cache_file_str = f"{cache_dir}{instance}.pkl"
        if Path(cache_file_str).is_file():
            with open(cache_file_str, "r") as f:
                morpho_values[pool] = pickle.load(open(cache_file_str, "rb"))
        else:
            end = end_cached
            print("retrieving morpho usd values for:", pool)
            morpho_values[pool] = {}
            start = end - epoch_duration
            n_snapshots = int(np.floor(epoch_duration / step_size))
            n = 1
            while end > start:
                block = get_block_from_timestamp(end)
                print(f"{n}\t/\t{n_snapshots}\t{block}")
                morpho_values[pool][block] = get_morpho_component_value(
                    pool=pool, timestamp=end
                )
                end -= step_size
                n += 1
            end = end_cached
            with open(cache_file_str, "wb") as f:
                pickle.dump(morpho_values[pool], f)
    return morpho_values


def determine_merit_breakdown(pools, end, step_size):
    end_cached = end
    merit_values = {}
    r = requests.get(AAVECHAN_MERIT_API)
    r.raise_for_status()
    raw_merit = r.json()
    for pool in pools:
        instance = f"{epoch_name}-{step_size}-{protocol}-{chain}-{pool}".replace(
            "/", "_"
        )
        cache_dir = "MaxiOps/merkl/cache/merit_usd/"
        os.makedirs(os.path.dirname(cache_dir), exist_ok=True)
        cache_file_str = f"{cache_dir}{instance}.pkl"
        if Path(cache_file_str).is_file():
            with open(cache_file_str, "r") as f:
                merit_values[pool] = pickle.load(open(cache_file_str, "rb"))
        else:
            end = end_cached
            print("retrieving merit usd values for:", pool)
            merit_values[pool] = {}
            start = end - epoch_duration
            n_snapshots = int(np.floor(epoch_duration / step_size))
            n = 1
            while end > start:
                block = get_block_from_timestamp(end)
                print(f"{n}\t/\t{n_snapshots}\t{block}")
                merit_values[pool][block] = get_merit_component_value(
                    pool=pool, timestamp=end, raw_merit=raw_merit
                )
                end -= step_size
                n += 1
            end = end_cached
            with open(cache_file_str, "wb") as f:
                pickle.dump(merit_values[pool], f)
    return merit_values


def get_morpho_component_value(pool, timestamp):
    # calculate the $ value of the morpho component(s) in a pool
    raw = subgraph.fetch_graphql_data(
        "apiv3",
        """query PoolTokens($poolId: String!, $chain: GqlChain!, $range: GqlPoolSnapshotDataRange!) {
            poolGetPool(id: $poolId, chain: $chain) {
                poolTokens {
                    address
                    balanceUSD
                    index
                }
            }
            poolGetSnapshots(id: $poolId, chain: $chain, range: $range) {
                amounts
                timestamp
            }
        }""",
        {"poolId": pool.lower(), "chain": CHAINS[chain], "range": "THIRTY_DAYS"},
    )
    value = Decimal(0)
    for component in raw["poolGetPool"]["poolTokens"]:
        try:
            if (
                drpc.eth.contract(
                    to_checksum_address(component["address"]),
                    abi=json.load(open("tools/python/abis/MetaMorphoV1_1.json")),
                )
                .functions.MORPHO()
                .call()
                == "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb"
            ):
                # this is a morpho component
                for snapshot in raw["poolGetSnapshots"]:
                    if snapshot["timestamp"] > timestamp:
                        balance = Decimal(snapshot["amounts"][int(component["index"])])
                        timestamp_eod = snapshot["timestamp"]
                        break
                else:
                    raise ValueError(
                        f"no snapshot found for {component['address']}! latest one found has timestamp {snapshot['timestamp']}"
                    )
                prices = subgraph.fetch_graphql_data(
                    "apiv3",
                    "get_historical_token_prices",
                    {
                        "addresses": [component["address"]],
                        "chain": CHAINS[chain],
                        "range": "THIRTY_DAY",
                    },
                )
                for entry in prices["tokenGetHistoricalPrices"][0]["prices"]:
                    if int(entry["timestamp"]) == timestamp_eod:
                        price = Decimal(entry["price"])
                        assert price > 0
                        break
                else:
                    raise ValueError(
                        f"no historical price found for morpho component {component['address']}!"
                    )
                value += balance * price
        except exceptions.ContractLogicError:
            continue
    return value


def get_merit_component_value(pool, timestamp, raw_merit):
    # calculate the $ value of the merit component(s) in a pool
    raw = subgraph.fetch_graphql_data(
        "apiv3",
        """query PoolTokens($poolId: String!, $chain: GqlChain!, $range: GqlPoolSnapshotDataRange!) {
            poolGetPool(id: $poolId, chain: $chain) {
                poolTokens {
                    address
                    balanceUSD
                    index
                }
            }
            poolGetSnapshots(id: $poolId, chain: $chain, range: $range) {
                amounts
                timestamp
            }
        }""",
        {"poolId": pool.lower(), "chain": CHAINS[chain], "range": "THIRTY_DAYS"},
    )
    value = Decimal(0)
    for component in raw["poolGetPool"]["poolTokens"]:
        is_merit_component = False

        # Check all campaigns for matching tokens
        for campaign in raw_merit:
            if isinstance(raw_merit[campaign], list) and len(raw_merit[campaign]) > 0:
                campaign_data = raw_merit[campaign][0]
                if (
                    "actionTokens" in campaign_data
                    and len(campaign_data["actionTokens"]) > 0
                ):
                    action_token = campaign_data["actionTokens"][0]
                    # Check if book exists and has STATA_TOKEN
                    if "book" in action_token and "STATA_TOKEN" in action_token["book"]:
                        if (
                            action_token["book"]["STATA_TOKEN"].lower()
                            == component["address"].lower()
                        ):
                            is_merit_component = True
                            break

        # Also check against watchlist addresses directly (for waBasGHO and similar tokens)
        if not is_merit_component and chain in WATCHLIST.get("merit", {}):
            for watchlist_addr in WATCHLIST["merit"][chain].keys():
                if watchlist_addr.lower() == component["address"].lower():
                    is_merit_component = True
                    break

        if is_merit_component:
            # this is a merit component
            for snapshot in raw["poolGetSnapshots"]:
                if snapshot["timestamp"] > timestamp:
                    balance = Decimal(snapshot["amounts"][int(component["index"])])
                    timestamp_eod = snapshot["timestamp"]
                    break
            else:
                raise ValueError(
                    f"no snapshot found for {component['address']}! latest one found has timestamp {snapshot['timestamp']}"
                )
            prices = subgraph.fetch_graphql_data(
                "apiv3",
                "get_historical_token_prices",
                {
                    "addresses": [component["address"]],
                    "chain": CHAINS[chain],
                    "range": "THIRTY_DAY",
                },
            )
            for entry in prices["tokenGetHistoricalPrices"][0]["prices"]:
                if int(entry["timestamp"]) == timestamp_eod:
                    price = Decimal(entry["price"])
                    assert price > 0
                    break
            else:
                raise ValueError(
                    f"no historical price found for merit component {component['address']}!"
                )
            value += balance * price
    return value


def consolidate_shares(df):
    consolidated = []
    for block in df.columns:
        if df[block].sum() == 0:
            consolidated.append(df[block])
        else:
            # calculate the percentage of the pool each user owns,
            # and weigh it by the total pool size of that block
            consolidated_block = (
                df[block].map(Decimal)
                / df[block].map(Decimal).sum()
                * Decimal(df.sum()[block])
            )
            consolidated.append(consolidated_block)
    consolidated = pd.concat(consolidated, axis=1)

    # sum the weighted percentages per user
    consolidated["total"] = consolidated.sum(axis=1).map(Decimal)
    # divide the weighted percentages by the sum of all weights
    consolidated["total"] = consolidated["total"] / Decimal(df.sum().sum())
    # round down until the sum of all weights is ~1
    n = Decimal("1e18")
    while consolidated["total"].sum() > 1:
        consolidated = np.trunc(n * consolidated) / n
        n -= 1
    assert consolidated["total"].sum() <= 1
    assert consolidated["total"].sum() == approx(
        Decimal(1.0), rel=Decimal(1e-6)
    ) or consolidated["total"].sum() == approx(Decimal(0.0), rel=Decimal(1e-6))
    return consolidated


def build_airdrop(reward_token, reward_total_wei, df):
    # https://docs.merkl.xyz/merkl-mechanisms/types-of-campaign/airdrop
    if reward_total_wei > 0:
        df[epoch_name] = (df["total"].map(Decimal) * Decimal(reward_total_wei)).apply(
            np.floor
        )
    else:
        df[epoch_name] = df["total"]
    df[epoch_name] = df[epoch_name].astype(str)
    df = df[df[epoch_name] != "0"]
    return {
        "rewardToken": reward_token,
        "rewards": df[[epoch_name]].to_dict(orient="index"),
    }


if __name__ == "__main__":
    step_size = 60 * 60
    session_beefy = Session()
    session_beefy.mount("https://", ADAPTER)
    for protocol in WATCHLIST:
        for chain in WATCHLIST[protocol]:
            if protocol == "merit":
                # https://apps.aavechan.com/api/merit/campaigns
                # replace date string with timestamp once it has passed and uncomment next string
                # drpc = Web3(Web3.HTTPProvider(f"https://lb.drpc.org/ogrpc?network={CHAIN_SLUGS['1']}&dkey={os.getenv('DRPC_KEY')}",session=session_drpc))
                # drpc.eth.get_block(23332300).timestamp

                if chain == "1":
                    epochs = [
                        1745348075,  # 22326470; start
                        1746566027,  # 22427270; end round 1
                        1747791815,  # 22528070; end round 2
                        1749010979,  # 22628870; end round 3
                        # 22729670,  # 22729670; end round 4
                        # 22830470,  # 22830470; end round 5
                        1752663107,  # 22931270; end round 4 + 5 + 6
                        1753869563,  # 23031200; end round 7
                        1755078491,  # 23131333, end round 8
                        1756286147,  # 23231500, end round 9
                        "23332300",  # 23332300; end round 10
                    ]
                elif chain == "43114":
                    epochs = [
                        0,
                        1745518679,  # 22340602; round 10
                        1750245275,  # 22731000; round 14
                        # 1751462483,  # 22831800; round 15; released together with 16
                        1752679127,  # 22932600; round 16
                        1753896131,  # 23033400; round 17
                        # 1755113051,  # 23134200; round 18
                        1755695435,  # 23182500, round 18 +19
                        1756902779,  # 23282608, round 20
                        "23382608",  # 23382608, round 21
                        # "23482608",  # 23482608, round 22
                    ]
                elif chain == "8453":
                    # Base chain epochs from base-supply-usdc, base-supply-gho, base-supply-eth-borrow-multiple campaigns
                    # Only including campaigns after block 22983001
                    # Note: These are Ethereum block numbers, not Base block numbers
                    epochs = [
                        1753287431,  # 22983001; start
                        1755981251,  # 23206201; end round 1 (rounds 5-7 for USDC, 1-3 for GHO/ETH)
                        "23422200",  # 23422200; end round 2
                        # "23638200",  # 23638200; end round 3
                    ]
                epoch_duration = epochs[-2] - epochs[-3]
            if protocol == "morpho":
                epoch_duration = 60 * 60 * 24 * 7
                first_epoch_end = 1737936000
                epochs = []
                ts = first_epoch_end
                while ts < int(datetime.now().timestamp()):
                    epochs.append(ts)
                    ts += epoch_duration
            epoch_name = f"epoch_{len(epochs) - 1}"
            print("epoch endings:", epochs)

            session_drpc = Session()
            session_drpc.mount("https://", ADAPTER)
            # breakpoint()
            drpc = Web3(
                Web3.HTTPProvider(
                    f"https://lb.drpc.org/ogrpc?network={CHAIN_SLUGS[chain]}&dkey={os.getenv('DRPC_KEY')}",
                    session=session_drpc,
                )
            )
            subgraph = Subgraph(CHAINS[chain].lower())
            for reward_token, rewards in WATCHLIST[protocol][chain].items():
                if rewards["claimable"] == "":
                    continue
                breakdown_needed = False
                for key, pool in rewards["pools"].items():
                    if pool["reward_wei"] == "":
                        breakdown_needed = True
                        break
                if breakdown_needed:
                    if protocol == "morpho":
                        breakdown_func = determine_morpho_breakdown
                    elif protocol == "merit":
                        breakdown_func = determine_merit_breakdown
                    # determine the $ value of the morpho component(s) in each pool
                    # this is used to weigh the user shares in the airdrop
                    protocol_usd_weights = breakdown_func(
                        pools=[pool["address"] for pool in rewards["pools"].values()],
                        end=epochs[-2],
                        step_size=step_size,
                    )
                    protocol_usd_block_totals = {}
                    protocol_usd_pool_totals = {}
                    for pool in protocol_usd_weights:
                        if pool not in protocol_usd_pool_totals:
                            protocol_usd_pool_totals[pool] = Decimal(0)
                        for block in protocol_usd_weights[
                            list(protocol_usd_weights)[0]
                        ]:
                            protocol_usd_pool_totals[pool] += protocol_usd_weights[
                                pool
                            ][block]
                            if block not in protocol_usd_block_totals:
                                protocol_usd_block_totals[block] = Decimal(0)
                            protocol_usd_block_totals[block] += protocol_usd_weights[
                                pool
                            ][block]
                    print(f"{protocol} usd pool totals:")
                    print(protocol_usd_pool_totals)

                    cumsum = Decimal(
                        sum([x for x in protocol_usd_pool_totals.values()])
                    )
                    wei_written = Decimal(0)
                    for pool, value in protocol_usd_pool_totals.items():
                        for key in rewards["pools"]:
                            if rewards["pools"][key]["address"] == pool:
                                rewards["pools"][key]["reward_wei"] = str(
                                    int(value / cumsum * Decimal(rewards["claimable"]))
                                )
                                wei_written += Decimal(
                                    rewards["pools"][key]["reward_wei"]
                                )
                    assert wei_written <= Decimal(rewards["claimable"])
                    with open(
                        "tools/python/gen_merkl_airdrops_watchlist.json", "w"
                    ) as f:
                        json.dump(WATCHLIST, f, indent=2)
                        f.write("\n")

                for pool in rewards["pools"]:
                    # skip pools with 0 rewards
                    if Decimal(rewards["pools"][pool]["reward_wei"]) == 0:
                        continue

                    address = rewards["pools"][pool]["address"]
                    instance = (
                        f"{epoch_name}-{step_size}-{protocol}-{chain}-{pool}".replace(
                            "/", "_"
                        )
                    )
                    print(instance)

                    cache_dir = "MaxiOps/merkl/cache/"
                    os.makedirs(os.path.dirname(cache_dir), exist_ok=True)
                    cache_file_str = f"{cache_dir}{instance}.pkl"
                    if Path(cache_file_str).is_file():
                        # use locally stored df
                        # delete local file beforehand to retrieve df from scratch!
                        df = pd.read_pickle(cache_file_str)
                    else:
                        # get bpt balances for a pool at different timestamps
                        df = build_snapshot_df(
                            pool=address,
                            end=epochs[-2],
                            step_size=step_size,
                        )

                        # ignore shares sent to zero address
                        df = df.drop(index=ZERO_ADDRESS, errors="ignore")

                        df.to_pickle(cache_file_str)

                    # consolidate user pool shares
                    df = consolidate_shares(df)
                    print(df)

                    # morpho takes a 50bips fee on json airdrops
                    if protocol in ["morpho", "merit"]:
                        reward_total_wei = int(
                            Decimal(rewards["pools"][pool]["reward_wei"])
                            * Decimal(1 - 0.005)
                        )
                    else:
                        reward_total_wei = int(rewards["pools"][pool]["reward_wei"])

                    # build airdrop object and dump to json file
                    airdrop = build_airdrop(
                        reward_token=reward_token,
                        reward_total_wei=reward_total_wei,
                        df=df,
                    )

                    # checksum
                    total = Decimal(0)
                    for user in airdrop["rewards"]:
                        total += Decimal(airdrop["rewards"][user][epoch_name])
                    if protocol == "morpho":
                        total /= Decimal(1 - 0.005)
                    assert total <= Decimal(rewards["pools"][pool]["reward_wei"])
                    print(
                        "expected dust:",
                        int(Decimal(rewards["pools"][pool]["reward_wei"]) - total),
                        Decimal(
                            int(Decimal(rewards["pools"][pool]["reward_wei"]) - total)
                            / Decimal(1e18)
                        ),
                    )

                    with open(
                        f"MaxiOps/merkl/airdrops/{instance}-{reward_token}.json", "w"
                    ) as f:
                        json.dump(airdrop, f, indent=2)
                        f.write("\n")
