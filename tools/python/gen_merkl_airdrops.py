import json
import os
import pickle
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
AURA_VOTER_PROXY = "0xaF52695E1bB01A16D33D7194C28C42b10e0Dbec2"
AURA_VOTER_PROXY_LITE = "0xC181Edc719480bd089b94647c2Dc504e2700a2B0"
BEEFY_PARTNER_BASE_URL = (
    "https://balance-api.beefy.finance/api/v1/partner/balancer/config"
)
CHAINS = {"1": "MAINNET", "8453": "BASE"}
CHAIN_SLUGS = {"1": "ethereum", "8453": "base"}
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
    r = session_beefy.get(
        BEEFY_PARTNER_BASE_URL + f"/{CHAIN_SLUGS[chain]}/{block}/bundles"
    )
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
    r = session_beefy.get(
        BEEFY_PARTNER_BASE_URL + f"/{CHAIN_SLUGS[chain]}/{block}/bundles"
    )
    r.raise_for_status()
    raw_beefy = r.json()
    for vault in raw_beefy:
        if vault["vault_config"]["undelying_lp_address"].lower() == pool.lower():
            return vault["vault_config"]["strategy_address"]
    return ""


def get_block_from_timestamp(ts):
    raw = subgraph.fetch_graphql_data(
        "blocks",
        "first_block_after_ts",
        {"timestamp_lt": ts + step_size, "timestamp_gt": ts - 1},
    )
    return int(raw["blocks"][0]["number"])


def build_snapshot_df(
    pool,  # pool address
    end,  # timestamp of the last snapshot
    step_size,  # amount of seconds between snapshots
):
    gauge = BalPoolsGauges(CHAINS[chain]).get_preferential_gauge(pool)
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
            gauge = gauge.lower()
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
    for block in pool_shares:
        total_shares[block] = {}
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
            except exceptions.BadFunctionCallOutput:
                if i < retries - 1:
                    continue
                else:
                    raise

    # build dataframe
    df = pd.DataFrame(total_shares).fillna(Decimal(0))

    # checksum total balances versus total supply
    assert df.sum().sum() == approx(
        sum(total_supply.values()) / Decimal(1e18), rel=Decimal(1e-6)
    )
    for block in df.columns:
        assert df[block].sum() == approx(
            total_supply[block] / Decimal(1e18), rel=Decimal(1e-6)
        )

    return df


def determine_morpho_breakdown(pools, end, step_size):
    end_cached = end
    morpho_values = {}
    for pool in pools:
        instance = f"{epoch_name}-{step_size}-{protocol}-{chain}-{pool}"
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
    assert consolidated["total"].sum() == approx(Decimal(1.0), rel=Decimal(1e-6))
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
        if protocol == "merit":
            # comment out once a month, not needed every week
            # continue
            # https://apps.aavechan.com/api/merit/campaigns
            # replace date string with timestamp once it has passed and uncomment next string
            # drpc.eth.get_block(22638003).timestamp
            epochs = [
                1733932799,  # 21558817
                1741163423,  # 21979500
                1743855959,  # 22202701
                1746462191,  # 22418702
                "~Thu Jun 05 2025 10:43:33UTC",  # 22638003
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
        for chain in WATCHLIST[protocol]:
            session_drpc = Session()
            session_drpc.mount("https://", ADAPTER)
            drpc = Web3(
                Web3.HTTPProvider(
                    f"https://lb.drpc.org/ogrpc?network={CHAIN_SLUGS[chain]}&dkey={os.getenv('DRPC_KEY')}",
                    session=session_drpc,
                )
            )
            subgraph = Subgraph(CHAINS[chain].lower())
            for reward_token, rewards in WATCHLIST[protocol][chain].items():
                breakdown_needed = False
                for key, pool in rewards["pools"].items():
                    if pool["reward_wei"] == "":
                        breakdown_needed = True
                        break
                if breakdown_needed:
                    # determine the $ value of the morpho component(s) in each pool
                    # this is used to weigh the user shares in the airdrop
                    morpho_usd_weights = determine_morpho_breakdown(
                        pools=[pool["address"] for pool in rewards["pools"].values()],
                        end=epochs[-2],
                        step_size=step_size,
                    )
                    morpho_usd_block_totals = {}
                    morpho_usd_pool_totals = {}
                    for pool in morpho_usd_weights:
                        if pool not in morpho_usd_pool_totals:
                            morpho_usd_pool_totals[pool] = Decimal(0)
                        for block in morpho_usd_weights[list(morpho_usd_weights)[0]]:
                            morpho_usd_pool_totals[pool] += morpho_usd_weights[pool][
                                block
                            ]
                            if block not in morpho_usd_block_totals:
                                morpho_usd_block_totals[block] = Decimal(0)
                            morpho_usd_block_totals[block] += morpho_usd_weights[pool][
                                block
                            ]
                    print("morpho usd pool totals:")
                    print(morpho_usd_pool_totals)

                    cumsum = Decimal(sum([x for x in morpho_usd_pool_totals.values()]))
                    wei_written = Decimal(0)
                    for pool, value in morpho_usd_pool_totals.items():
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
                    address = rewards["pools"][pool]["address"]
                    instance = f"{epoch_name}-{step_size}-{protocol}-{chain}-{pool}"
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
