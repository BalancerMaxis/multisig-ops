import os

import pandas as pd
from dune_client.client import DuneClient
from dune_client.types import QueryParameter
from dune_client.query import QueryBase

dune = DuneClient.from_env()


def get_upkeeps(chain="ethereum"):
    query = QueryBase(
        name="@gosuto/cla_chain_upkeeps",
        query_id=3889683,
        params=[
            QueryParameter.enum_type(name="chain", value=chain),
        ],
    )
    return dune.run_query_dataframe(query)


if __name__ == "__main__":
    dfs = []
    for chain in [
        "ethereum",
        "arbitrum",
        "polygon",
        "optimism",
        "avalanche_c",
        "base",
        "gnosis",
    ]:
        dfs.append(get_upkeeps(chain))
    dfs = pd.concat(dfs)
    dfs.to_csv("../../upkeeps.csv", index=False)
