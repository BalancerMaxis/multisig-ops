from bal_tools import Subgraph


CHAINS = ["arbitrum", "base", "gnosis", "mainnet", "sepolia"]


for chain in CHAINS:
    print(chain)
    pools = Subgraph(chain).fetch_graphql_data(
        "apiv3", "get_pools", {"chain": chain.upper()}
    )["poolGetPools"]

    for pool in pools:
        if pool["protocolVersion"] == 3:
            print(pool["address"])
