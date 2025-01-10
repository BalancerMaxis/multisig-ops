import json
import os
import pytest
from datetime import datetime
from decimal import Decimal

import numpy as np
import pandas as pd
from web3 import Web3, exceptions

from bal_tools import Subgraph


WATCHLIST = {
    "0x58D97B57BB95320F9a05dC918Aef65434969c2B2": [  # morpho
        "0x10A04efbA5B880e169920Fd4348527C64FB29d4D"  # csUSDC-csUSDT
    ],
    "0x030bA81f1c18d280636F32af80b9AAd02Cf0854e": [  # aweth
        "0xc4Ce391d82D164c166dF9c8336DDF84206b2F812"  # waEthLidoWETH-waEthLidowstETH
    ],
}
SUBGRAPH = Subgraph()
W3 = Web3(
    Web3.HTTPProvider(
        f"https://lb.drpc.org/ogrpc?network=ethereum&dkey={os.getenv('DRPC_KEY')}"
    )
)

# dev
GAUGES = {
    "0x10A04efbA5B880e169920Fd4348527C64FB29d4D": "0x5bBaeD1fADC08C5fb3e4ae3C8848777E2dA77103",
    "0xc4Ce391d82D164c166dF9c8336DDF84206b2F812": "0x4B891340b51889f438a03DC0e8aAAFB0Bc89e7A6",
}
LATEST_TS = int(datetime.now().timestamp())


def get_user_shares_pool(pool, block):
    query = """query PoolShares($where: PoolShare_filter, $block: Block_height) {
        poolShares(where: $where, block: $block) {
            user {
                id
            }
            balance
        }
    }"""
    params = {
        "where": {
            "balance_gt": 0.001,
            "pool": pool,
        },
        "block": {"number": block},
    }
    raw = SUBGRAPH.fetch_graphql_data(
        "subgraphs-v3",
        query,
        params,
        url="https://api.studio.thegraph.com/query/75376/balancer-v3/version/latest",
    )
    return dict([(x["user"]["id"], Decimal(x["balance"])) for x in raw["poolShares"]])


def get_user_shares_gauge(gauge, block):
    query = """query GaugeShares($where: GaugeShare_filter, $block: Block_height) {
        gaugeShares(where: $where, block: $block) {
            user {
                id
            }
            balance
        }
    }"""
    params = {
        "where": {
            "balance_gt": 0.001,
            "gauge": gauge,
        },
        "block": {"number": block},
    }
    raw = SUBGRAPH.fetch_graphql_data("gauges", query, params)
    return dict([(x["user"]["id"], Decimal(x["balance"])) for x in raw["gaugeShares"]])


def get_block_from_timestamp(ts):
    query = """query GetBlockFromTimestamp($where: Block_filter) {
        blocks(orderBy: "number", orderDirection: "desc", where: $where) {
            number
            timestamp
        }
    }"""
    params = {"where": {"timestamp_lte": ts}}
    raw = SUBGRAPH.fetch_graphql_data(
        "blocks",
        query,
        params,
        url="https://api.studio.thegraph.com/query/48427/ethereum-blocks/version/latest",
    )
    return int(raw["blocks"][0]["number"])


def build_snapshot_df(
    pool,  # pool address
    end,  # timestamp of the last snapshot
    n=7,  # amount of snapshots
    step_size=60 * 60 * 24,  # amount of seconds between snapshots
):
    # TODO: lookup gauge from pool
    gauge = GAUGES[pool]

    # get user shares for pool and gauge at different timestamps
    pool_shares = {}
    gauge_shares = {}
    for _ in range(n):
        block = get_block_from_timestamp(end)
        pool_shares[block] = get_user_shares_pool(pool=pool, block=block)
        gauge_shares[block] = get_user_shares_gauge(gauge=gauge, block=block)
        end -= step_size

    # calculate total shares per user per block
    total_shares = {}
    total_supply = {}
    for block in pool_shares:
        total_shares[block] = {}
        for user_id in pool_shares[block]:
            if user_id == gauge:
                # we do not want to count the gauge as a user
                continue
            total_shares[block][user_id] = pool_shares[block][user_id]
        for user_id in gauge_shares[block]:
            if user_id not in total_shares[block]:
                total_shares[block][user_id] = gauge_shares[block][user_id]
            else:
                total_shares[block][user_id] += gauge_shares[block][user_id]
        # collect onchain total supply per block
        contract = W3.eth.contract(
            address=Web3.to_checksum_address(pool),
            abi=json.load(open("tools/python/abis/StablePoolV3.json")),
        )
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


def consolidate_shares(df):
    consolidated = pd.DataFrame()
    for block in df.columns:
        if df[block].sum() == 0:
            consolidated[block] = 0
        else:
            # calculate the percentage of the pool each user owns
            consolidated[block] = df[block] / df[block].sum()
            # weigh it by the total pool size of that block
            consolidated[block] *= df.sum()[block]
    # sum the weighted percentages per user
    consolidated["total"] = consolidated.sum(axis=1)
    # divide the weighted percentages by the sum of all weights
    consolidated["total"] = consolidated["total"] / df.sum().sum()
    return consolidated


def build_airdrop(reward_token, reward_total_wei, df):
    # https://docs.merkl.xyz/merkl-mechanisms/types-of-campaign/airdrop
    df["wei"] = df["total"] * reward_total_wei
    df["wei"] = df["wei"].apply(np.floor).astype(int).astype(str)
    return {"rewardToken": reward_token, "rewards": df[["wei"]].to_dict(orient="index")}


if __name__ == "__main__":
    for reward_token in WATCHLIST:
        for pool in WATCHLIST[reward_token]:
            # get bpt balances for a pool at different timestamps
            df = build_snapshot_df(pool=pool, end=LATEST_TS)
            df.to_csv("tools/python/df_snapshot.csv")

            # consolidate user pool shares
            df = consolidate_shares(df)
            df.to_csv("tools/python/df_consolidated.csv")

            # build airdrop object and dump to json file
            airdrop = build_airdrop(
                reward_token=reward_token, reward_total_wei=1e18, df=df
            )
            json.dump(airdrop, open(f"airdrop-{pool}.json", "w"), indent=2)
