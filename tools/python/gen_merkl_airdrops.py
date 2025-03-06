import json
import os
import pytest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
from requests import Session
from requests.adapters import HTTPAdapter, Retry
from web3 import Web3, exceptions

from bal_addresses.addresses import ZERO_ADDRESS, to_checksum_address
from bal_tools import Subgraph, BalPoolsGauges


WATCHLIST = json.load(open("tools/python/gen_merkl_airdrops_watchlist.json"))
SUBGRAPH = Subgraph()
EPOCH_DURATION = 60 * 60 * 24 * 7
FIRST_EPOCH_END = 1737936000
AURA_VOTER_PROXY = "0xaF52695E1bB01A16D33D7194C28C42b10e0Dbec2"
AURA_VOTER_PROXY_LITE = "0xC181Edc719480bd089b94647c2Dc504e2700a2B0"
BEEFY_PARTNER_BASE_URL = (
    "https://balance-api.beefy.finance/api/v1/partner/balancer/config"
)
CHAINS = {"1": "MAINNET"}

adapter = HTTPAdapter(
    pool_connections=20,
    pool_maxsize=20,
    max_retries=Retry(
        total=10, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504, 520]
    ),
)
session_drpc = Session()
session_drpc.mount("https://", adapter)
drpc = Web3(
    Web3.HTTPProvider(
        f"https://lb.drpc.org/ogrpc?network=ethereum&dkey={os.getenv('DRPC_KEY')}",
        session=session_drpc,
    )
)
session_beefy = Session()
session_beefy.mount("https://", adapter)

EPOCHS = []
ts = FIRST_EPOCH_END
while ts < int(datetime.now().timestamp()):
    EPOCHS.append(ts)
    ts += EPOCH_DURATION
epoch_name = f"epoch_{len(EPOCHS) - 1}"
print("epoch endings:", EPOCHS)


def get_user_shares_pool(pool, block):
    raw = SUBGRAPH.fetch_graphql_data(
        "vault-v3",
        "get_user_shares_by_pool",
        {"pool": pool.lower(), "block": block},
    )
    return dict([(x["user"]["id"], Decimal(x["balance"])) for x in raw["poolShares"]])


def get_user_shares_gauge(gauge, block):
    raw = SUBGRAPH.fetch_graphql_data(
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
    raw = SUBGRAPH.fetch_graphql_data(
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
    r = session_beefy.get(BEEFY_PARTNER_BASE_URL + f"/ethereum/{block}/bundles")
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
    r = session_beefy.get(BEEFY_PARTNER_BASE_URL + f"/ethereum/{block}/bundles")
    r.raise_for_status()
    raw_beefy = r.json()
    for vault in raw_beefy:
        if vault["vault_config"]["undelying_lp_address"].lower() == pool.lower():
            return vault["vault_config"]["strategy_address"]
    return ""


def get_block_from_timestamp(ts):
    raw = SUBGRAPH.fetch_graphql_data(
        "blocks",
        "first_block_after_ts",
        {"timestamp_lt": "9123456789", "timestamp_gt": ts - 1},
    )
    return int(raw["blocks"][0]["number"])


def build_snapshot_df(
    pool,  # pool address
    end,  # timestamp of the last snapshot
    step_size,  # amount of seconds between snapshots
):
    gauge = BalPoolsGauges().get_preferential_gauge(pool)
    beefy_strat = get_beefy_strat(pool, get_block_from_timestamp(end)).lower()

    # get user shares for pool and gauge at different timestamps
    pool_shares = {}
    gauge_shares = {}
    aura_shares = {}
    beefy_shares = {}
    start = end - EPOCH_DURATION
    n_snapshots = int(np.floor(EPOCH_DURATION / step_size))
    n = 1
    while end > start:
        block = get_block_from_timestamp(end)
        print(f"{n}\t/\t{n_snapshots}\t{block}")
        pool_shares[block] = get_user_shares_pool(pool=pool, block=block)
        gauge_shares[block] = get_user_shares_gauge(gauge=gauge, block=block)
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
                gauge.lower(),
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
        try:
            total_supply[block] = contract.functions.totalSupply().call(
                block_identifier=block
            )
        except exceptions.BadFunctionCallOutput:
            total_supply[block] = 0

    # build dataframe
    df = pd.DataFrame(total_shares, dtype=float).fillna(0)

    # checksum total balances versus total supply
    assert df.sum().sum() == pytest.approx(sum(total_supply.values()) / 1e18, rel=1e-6)
    for block in df.columns:
        assert df[block].sum() == pytest.approx(total_supply[block] / 1e18, rel=1e-6)

    return df


def determine_morpho_breakdown(pools, end, step_size):
    end_cached = end
    morpho_values = {}
    for pool in pools:
        print("retrieving morpho usd values for:", pool)
        morpho_values[pool] = {}
        start = end - EPOCH_DURATION
        n_snapshots = int(np.floor(EPOCH_DURATION / step_size))
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
    return morpho_values


def get_morpho_component_value(pool, timestamp):
    # calculate the $ value of the morpho component(s) in a pool
    raw = SUBGRAPH.fetch_graphql_data(
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
    value = 0
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
                        balance = float(snapshot["amounts"][int(component["index"])])
                        timestamp_eod = snapshot["timestamp"]
                        break
                else:
                    balance = 0
                prices = SUBGRAPH.fetch_graphql_data(
                    "apiv3",
                    "get_historical_token_prices",
                    {
                        "addresses": [component["address"]],
                        "chain": CHAINS[chain],
                        "range": "THIRTY_DAY",
                    },
                )
                if balance > 0:
                    for entry in prices["tokenGetHistoricalPrices"][0]["prices"]:
                        if int(entry["timestamp"]) == timestamp_eod:
                            price = entry["price"]
                            break
                    else:
                        raise ValueError(
                            f"no historical price found for morpho component {component['address']}!"
                        )
                    value += float(balance) * float(price)
        except exceptions.ContractLogicError:
            continue
    return value


def consolidate_shares(df, usd_weights=None, usd_totals=None):
    consolidated = []
    for block in df.columns:
        if df[block].sum() == 0:
            consolidated.append(df[block])
        else:
            # calculate the percentage of the pool each user owns,
            # and weigh it by the total pool size of that block
            consolidated_block = df[block] / df[block].sum() * df.sum()[block]
            if usd_weights and usd_totals:
                # weigh by the $ values for this pool
                consolidated_block = consolidated_block * usd_weights[block]
            consolidated.append(consolidated_block)
    consolidated = pd.concat(consolidated, axis=1)

    # sum the weighted percentages per user
    consolidated["total"] = consolidated.sum(axis=1)
    # divide the weighted percentages by the sum of all weights
    consolidated["total"] = consolidated["total"] / df.sum().sum()
    if usd_weights and usd_totals:
        # divide by the sum of the $ value of all pools
        consolidated["total"] = consolidated["total"] / sum(usd_totals.values())
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
    for protocol in WATCHLIST:
        # TODO: aave not implemented yet
        if protocol == "aave":
            break
        for chain in WATCHLIST[protocol]:
            # TODO: other chains not implemented yet
            if chain != "1":
                break
            if protocol == "morpho":
                # determine the $ value of the morpho component(s) in each pool
                # this is used to weigh the user shares in the airdrop
                morpho_usd_weights = determine_morpho_breakdown(
                    pools=[
                        pool["address"]
                        for pool in WATCHLIST[protocol][chain]["pools"].values()
                    ],
                    end=EPOCHS[-1],
                    step_size=step_size * 24,
                )
                morpho_usd_block_totals = {}
                morpho_usd_pool_totals = {}
                for pool in morpho_usd_weights:
                    if pool not in morpho_usd_pool_totals:
                        morpho_usd_pool_totals[pool] = 0
                    for block in morpho_usd_weights[list(morpho_usd_weights)[0]]:
                        morpho_usd_pool_totals[pool] += morpho_usd_weights[pool][block]
                        if block not in morpho_usd_block_totals:
                            morpho_usd_block_totals[block] = 0
                        morpho_usd_block_totals[block] += morpho_usd_weights[pool][
                            block
                        ]
                print("morpho usd pool totals:")
                print(morpho_usd_pool_totals)
                print("morpho usd block totals:")
                print(morpho_usd_block_totals)
                # break  # break here and set wei amounts in watchlist json on first run

            for pool in WATCHLIST[protocol][chain]["pools"]:
                address = WATCHLIST[protocol][chain]["pools"][pool]["address"]
                instance = f"{epoch_name}-{protocol}-{chain}-{pool}"
                print(instance)

                cache_file_str = f"MaxiOps/merkl/cache/{instance}.pkl"
                if Path(cache_file_str).is_file():
                    # use locally stored df
                    # delete local file beforehand to retrieve df from scratch!
                    df = pd.read_pickle(cache_file_str)
                else:
                    # get bpt balances for a pool at different timestamps
                    df = build_snapshot_df(
                        pool=address,
                        end=EPOCHS[-1],
                        step_size=step_size,
                    )

                    # ignore shares sent to zero address
                    df = df.drop(index=ZERO_ADDRESS, errors="ignore")

                    # consolidate user pool shares
                    df = consolidate_shares(
                        df,
                        (morpho_usd_weights[address] if protocol == "morpho" else None),
                        morpho_usd_block_totals if protocol == "morpho" else None,
                    )
                    df.to_pickle(cache_file_str)
                print(df)

                # morpho takes a 50bips fee on json airdrops
                if protocol == "morpho":
                    reward_total_wei = int(
                        Decimal(WATCHLIST[protocol][chain]["pools"][pool]["reward_wei"])
                        * Decimal(1 - 0.005)
                    )
                else:
                    reward_total_wei = int(
                        WATCHLIST[protocol][chain]["pools"][pool]["reward_wei"]
                    )

                # build airdrop object and dump to json file
                airdrop = build_airdrop(
                    reward_token=WATCHLIST[protocol][chain]["reward_token"],
                    reward_total_wei=reward_total_wei,
                    df=df,
                )

                if reward_total_wei == 0:
                    # tag the instance as a dry run for the resulting airdrop json
                    instance += "-dry"
                else:
                    # checksum
                    total = Decimal(0)
                    for user in airdrop["rewards"]:
                        total += Decimal(airdrop["rewards"][user][epoch_name])
                    if protocol == "morpho":
                        total *= Decimal(1 - 0.005)
                    assert total <= Decimal(
                        WATCHLIST[protocol][chain]["pools"][pool]["reward_wei"]
                    )
                    print(
                        "expected dust:",
                        int(
                            Decimal(
                                WATCHLIST[protocol][chain]["pools"][pool]["reward_wei"]
                            )
                            - total
                        ),
                        Decimal(
                            int(
                                Decimal(
                                    WATCHLIST[protocol][chain]["pools"][pool][
                                        "reward_wei"
                                    ]
                                )
                                - total
                            )
                            / Decimal(1e18)
                        ),
                    )

                with open(f"MaxiOps/merkl/airdrops/{instance}.json", "w") as f:
                    json.dump(airdrop, f, indent=2)
                    f.write("\n")
