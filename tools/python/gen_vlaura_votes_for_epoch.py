import json

import pandas as pd
import requests
from dune_client.client import DuneClient
from dune_client.types import QueryParameter
from dune_client.query import QueryBase

from helpers import get_subgraph_url


dune = DuneClient.from_env()


def get_df_revenue(start="2023-11-29 00:00:00", end="2023-12-13 00:00:00"):
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
    with open("../../config/core_pools.json") as f:
        config = json.load(f)

    result = []
    for chain in config:
        url = get_subgraph_url(chain)
        query = f"""{{
            pools(
                where: {{
                    priceRateProviders_: {{
                        address_not: "0x0000000000000000000000000000000000000000"}},
                        poolType_contains_nocase: "stable"
                }}
            ) {{
                address
            }}
        }}"""
        r = requests.post(url, json={"query": query})
        r.raise_for_status()
        for pool in r.json()["data"]["pools"]:
            result.append(pool["address"])
    return result


def main():
    # get all revenue data for a given epoch
    df = get_df_revenue()

    # dev: uncomment to use cached data in dev mode
    # df.to_csv("cache.csv", index=False)
    # df = pd.read_csv("cache.csv")

    # clean data
    df = df.rename(columns={"protocol_fee_collected": "revenue"})
    df = df[df["revenue"] != "<nil>"]
    df["revenue"] = df["revenue"].astype(float)

    # filter out optimism
    df = df[df["blockchain"] != "optimism"]

    # keep only stable pools with a rate provider
    sustainable_pools = get_stable_pools_with_rate_provider()
    df = df[df["pool_address"].isin(sustainable_pools)]

    # get top 6 pools by revenue
    df = df.sort_values(by=["revenue"], ascending=False).head(6)

    # add column with share of total revenue
    total_revenue = df["revenue"].sum()
    df["share"] = df["revenue"] / total_revenue

    print(df.to_markdown(index=False))


if __name__ == "__main__":
    main()
