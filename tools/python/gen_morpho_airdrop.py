import json

import numpy as np
import pandas as pd

from bal_tools import Subgraph


SUBGRAPH = Subgraph()
MORPHO = "0x58D97B57BB95320F9a05dC918Aef65434969c2B2"


def get_user_shares(pool, block):
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
    return dict([(x["user"]["id"], x["balance"]) for x in raw["poolShares"]])


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
    shares = {}
    for _ in range(n):
        block = get_block_from_timestamp(end)
        shares[block] = get_user_shares(pool=pool, block=block)
        end -= step_size
    return pd.DataFrame(shares, dtype=float).fillna(0)


def consolidate_shares(df):
    consolidated = pd.DataFrame()
    for block in df.columns:
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
    # get bpt balances for a pool at different timestamps
    df = build_snapshot_df(
        pool="0x89bb794097234e5e930446c0cec0ea66b35d7570", end=1734393600
    )
    # consolidate user pool shares
    df = consolidate_shares(df)
    # build airdrop object and dump to json file
    airdrop = build_airdrop(reward_token=MORPHO, reward_total_wei=1e18, df=df)
    json.dump(airdrop, open("airdrop.json", "w"), indent=2)