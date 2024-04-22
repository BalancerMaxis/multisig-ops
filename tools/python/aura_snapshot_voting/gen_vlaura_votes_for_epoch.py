import json
import os
import sys

import pandas as pd
import requests
from dune_client.client import DuneClient
from dune_client.types import QueryParameter
from dune_client.query import QueryBase
from bal_addresses.subgraph import Subgraph


dune = DuneClient.from_env()


def _get_prop_and_determine_date_range():
    # https://docs.aura.finance/aura/governance/gauge-voting#gauge-voting-rules-and-information
    query = """{
        proposals(
            where: {
                space: "gauges.aurafinance.eth"
            },
            orderBy: "created",
            orderDirection: desc
        ) {
            id
            title
            start
            end
            state
            choices
        }
    }"""
    r = requests.post("https://hub.snapshot.org/graphql", json={"query": query})
    r.raise_for_status()

    # make sure we grab an actual biweekly gauge vote prop
    for prop in r.json()["data"]["proposals"]:
        if "Gauge Weight for Week of " in prop["title"]:
            print(f'latest proposal is: "{prop["title"]}" ({prop["id"]})')
            break

    if prop["state"] == "active":
        # date range should be the 14 days right before the prop started
        end = prop["start"]
        start = end - 2 * 7 * 24 * 60 * 60
    else:
        # date range should be the start of the last prop up until now
        # NOTE: this is only to check what the running vote looks like; not final!
        end = int(pd.Timestamp.now(tz="UTC").timestamp())
        start = prop["start"]

    # convert timestamps to string (localised to utc but drop offset from the string)
    start = str(pd.to_datetime(start, unit="s").tz_localize("UTC"))[:-6]
    end = str(pd.to_datetime(end, unit="s").tz_localize("UTC"))[:-6]

    print(f"date range: {start} - {end}")
    return prop, start, end


def get_df_revenue(start="2023-12-07 02:00:00", end="2023-12-21 02:00:00"):
    query = QueryBase(
        name="@balancer / Protocol Fee Collected",
        query_id=3293596,
        params=[
            QueryParameter.date_type(name="1. Start Date", value=start),
            QueryParameter.date_type(name="2. End Date", value=end),
            QueryParameter.enum_type(name="3. Blockchain", value="All"),
        ],
    )
    return dune.run_query_dataframe(query)


def get_stable_pools_with_rate_provider():
    # leverage core pools config for chain labels
    with open("../../../config/core_pools.json") as f:
        config = json.load(f)

    result = []
    for chain in config:
        url = Subgraph(chain).get_subgraph_url("core")
        query = """{
            pools(
                first: 1000,
                where: {
                    and: [
                        {
                            priceRateProviders_: {
                                address_not: "0x0000000000000000000000000000000000000000"
                            }
                        },
                        {
                            or: [
                                {poolType_contains_nocase: "stable"},
                                {poolType_contains_nocase: "gyro"}
                            ]
                        }
                    ]
                }
            ) {
                address,poolType
            }
        }"""
        r = requests.post(url, json={"query": query})
        r.raise_for_status()
        for pool in r.json()["data"]["pools"]:
            result.append(pool["address"])
    return result


def get_core_pools():
    with open("../../../config/core_pools.json") as f:
        config = json.load(f)

    return [pool[:42] for chain in config for pool in config[chain]]


def gen_rev_data():
    # get all revenue data for a given epoch
    prop, start, end = _get_prop_and_determine_date_range()

    # dev: uncomment to use cached data in dev mode (and save dune credits)
    # df = pd.read_csv("cache.csv")

    df = get_df_revenue(start, end)
    # df.to_csv("cache.csv", index=False)

    # clean data
    df = df.rename(columns={"protocol_fee_collected": "revenue"})
    df = df[df["revenue"] != "<nil>"]
    df["revenue"] = df["revenue"].astype(float)

    # filter out optimism
    df = df[df["blockchain"] != "optimism"]

    # keep only stable pools with a rate provider
    sustainable_pools = get_stable_pools_with_rate_provider()
    core_pools = [p for p in get_core_pools() if p not in sustainable_pools]

    df["type"] = df["pool_address"].apply(
        lambda x: (
            "sustainable"
            if x in sustainable_pools
            else "core" if x in core_pools else "NA"
        )
    )

    # df = df.dropna(subset=["type"])
    df = df.sort_values(by=["revenue"], ascending=False)

    return df, prop
