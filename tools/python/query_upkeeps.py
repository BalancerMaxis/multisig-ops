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
    raw = dune.run_query_csv(query).data
    with open('dirty.tmp', 'wb') as f:
        f.write(raw.getbuffer())
    with open('clean.tmp', 'w') as f:
        buffer = open('dirty.tmp').read()
        for sanitise in ['\x00', '\x10', '\x1a', '\x1b', '\x1c', '\x1d', '\x1e', '\x1f']:
            buffer = buffer.replace(sanitise, '')
        f.write(buffer)
    return pd.read_csv('clean.tmp')


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
    dfs['upkeep_name'] = dfs['upkeep_name'].str.strip()
    dfs.to_csv("../../upkeeps.csv", index=False)
