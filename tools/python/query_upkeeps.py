import pandas as pd
from dune_client.client import DuneClient
from dune_client.types import QueryParameter
from dune_client.query import QueryBase


def get_upkeeps(chain='ethereum'):
    dune = DuneClient.from_env()
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
    for chain in ['ethereum', 'arbitrum', 'polygon', 'optimism', 'avalanche', 'base', 'gnosis']:
        dfs.append(get_upkeeps(chain))
    pd.concat(dfs).to_csv('../../out/upkeeps.csv', index=False)
