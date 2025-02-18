import json
import os
import pytest
from datetime import datetime
from decimal import Decimal

import requests
import numpy as np
import pandas as pd
from web3 import Web3, exceptions

from bal_tools import Subgraph, BalPoolsGauges


WATCHLIST = json.load(open("tools/python/gen_merkl_airdrops_watchlist.json"))
SUBGRAPH = Subgraph()
W3 = Web3(
    Web3.HTTPProvider(
        f"https://lb.drpc.org/ogrpc?network=ethereum&dkey={os.getenv('DRPC_KEY')}"
    )
)
EPOCH_DURATION = 60 * 60 * 24 * 14
FIRST_EPOCH_END = 1737936000
AURA_VOTER_PROXY = "0xaF52695E1bB01A16D33D7194C28C42b10e0Dbec2"
AURA_VOTER_PROXY_LITE = "0xC181Edc719480bd089b94647c2Dc504e2700a2B0"
BEEFY_PARTNER_BASE_URL = (
    "https://balance-api.beefy.finance/api/v1/partner/balancer/config"
)

EPOCHS = []
ts = FIRST_EPOCH_END
while ts < int(datetime.now().timestamp()):
    EPOCHS.append(ts)
    ts += EPOCH_DURATION
epoch_name = f"epoch_{len(EPOCHS)}"
print("epochs:", EPOCHS)
print(epoch_name)


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
            "pool": pool.lower(),
        },
        "block": {"number": block},
    }
    raw = SUBGRAPH.fetch_graphql_data(
        "subgraphs-v3",
        query,
        params,
        url="https://api.studio.thegraph.com/query/75376/balancer-v3/version/latest",
        retries=5,
    )
    return dict([(x["user"]["id"], Decimal(x["balance"])) for x in raw["poolShares"]])


def get_user_shares_gauge(gauge, block):
    raw = SUBGRAPH.fetch_graphql_data(
        "gauges",
        "fetch_gauge_shares",
        {"gaugeAddress": gauge, "block": block},
    )
    return dict([(x["user"]["id"], Decimal(x["balance"])) for x in raw["gaugeShares"]])


def get_user_shares_aura(pool, block):
    query = """query Pools($where: Pool_filter, $block: Block_height, $staked: PoolAccount_filter) {
        pools(where: $where, block: $block) {
            accounts(where: $staked) {
                account {
                    id
                }
                staked
            }
        }
    }"""
    params = {
        "where": {"lpToken": pool.lower()},
        "block": {"number": block},
        "staked": {"staked_gt": 0},
    }
    raw = SUBGRAPH.fetch_graphql_data("aura", query, params)
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
    r = requests.get(BEEFY_PARTNER_BASE_URL + f"/ethereum/{block}/bundles")
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


def get_beefy_strat(pool, block):
    r = requests.get(BEEFY_PARTNER_BASE_URL + f"/ethereum/{block}/bundles")
    r.raise_for_status()
    raw_beefy = r.json()
    for vault in raw_beefy:
        if vault["vault_config"]["undelying_lp_address"].lower() == pool.lower():
            return vault["vault_config"]["strategy_address"]


def get_block_from_timestamp(ts):
    query = """query GetBlockFromTimestamp($where: Block_filter) {
        blocks(orderBy: "number", orderDirection: "desc", where: $where) {
            number
            timestamp
        }
    }"""
    params = {"where": {"timestamp_lte": ts}}
    raw = SUBGRAPH.fetch_graphql_data("blocks", query, params)
    return int(raw["blocks"][0]["number"])


def build_snapshot_df(
    pool,  # pool address
    end,  # timestamp of the last snapshot
    step_size=60 * 60,  # amount of seconds between snapshots
):
    gauge = BalPoolsGauges().get_preferential_gauge(pool)
    beefy_strat = get_beefy_strat(pool, get_block_from_timestamp(end)).lower()

    # get user shares for pool and gauge at different timestamps
    pool_shares = {}
    gauge_shares = {}
    aura_shares = {}
    beefy_shares = {}
    start = end - EPOCH_DURATION
    while end > start:
        block = get_block_from_timestamp(end)
        pool_shares[block] = get_user_shares_pool(pool=pool, block=block)
        gauge_shares[block] = get_user_shares_gauge(gauge=gauge, block=block)
        aura_shares[block] = get_user_shares_aura(pool=pool, block=block)
        beefy_shares[block] = get_user_shares_beefy(pool=pool, block=block)
        end -= step_size

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
    consolidated = []
    for block in df.columns:
        if df[block].sum() == 0:
            consolidated.append(df[block])
        else:
            # calculate the percentage of the pool each user owns,
            # and weigh it by the total pool size of that block
            consolidated.append(df[block] / df[block].sum() * df.sum()[block])
    consolidated = pd.concat(consolidated, axis=1)
    # sum the weighted percentages per user
    consolidated["total"] = consolidated.sum(axis=1)
    # divide the weighted percentages by the sum of all weights
    consolidated["total"] = consolidated["total"] / df.sum().sum()
    return consolidated


def build_airdrop(reward_token, reward_total_wei, df):
    # https://docs.merkl.xyz/merkl-mechanisms/types-of-campaign/airdrop
    df[epoch_name] = df["total"].map(Decimal) * Decimal(reward_total_wei)
    df[epoch_name] = df[epoch_name].apply(np.floor).astype(str)
    df = df[df[epoch_name] != "0"]
    return {
        "rewardToken": reward_token,
        "rewards": df[[epoch_name]].to_dict(orient="index"),
    }


if __name__ == "__main__":
    for protocol in WATCHLIST:
        # TODO: aave not implemented yet
        if protocol == "aave":
            break
        for pool in WATCHLIST[protocol]["pools"]:
            print(protocol, pool)

            # get bpt balances for a pool at different timestamps
            df = build_snapshot_df(
                pool=WATCHLIST[protocol]["pools"][pool]["address"], end=EPOCHS[-1]
            )

            # consolidate user pool shares
            df = consolidate_shares(df)
            print(df)

            # morpho takes a 50bips fee on json airdrops
            if protocol == "morpho":
                reward_total_wei = int(
                    Decimal(WATCHLIST[protocol]["pools"][pool]["reward_wei"])
                    * Decimal(1 - 0.005)
                )
            else:
                reward_total_wei = int(WATCHLIST[protocol]["pools"][pool]["reward_wei"])

            # build airdrop object and dump to json file
            airdrop = build_airdrop(
                reward_token=WATCHLIST[protocol]["reward_token"],
                reward_total_wei=reward_total_wei,
                df=df,
            )

            # checksum
            total = Decimal(0)
            for user in airdrop["rewards"]:
                total += Decimal(airdrop["rewards"][user][epoch_name])
            assert total <= Decimal(WATCHLIST[protocol]["pools"][pool]["reward_wei"])
            print(
                "dust:",
                Decimal(reward_total_wei) - total,
            )

            json.dump(
                airdrop,
                open(
                    f"MaxiOps/merkl/airdrops/{protocol}-{pool}-{epoch_name}.json", "w"
                ),
                indent=2,
            )
