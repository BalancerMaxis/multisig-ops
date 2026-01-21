from bal_tools import Subgraph

CHAINS = ["arbitrum", "base", "gnosis", "mainnet", "sepolia"]


for chain in CHAINS:
    print(chain)
    pools = Subgraph(chain).fetch_graphql_data(
        "pools-v3", "get_ordered_pools", {"chain": chain.upper()}
    )["pools"]

    for pool in pools:
        print(pool["address"])
