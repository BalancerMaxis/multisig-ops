from bal_tools import Subgraph


SUBGRAPH = Subgraph()


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


def build_airdrop():
    # https://docs.merkl.xyz/merkl-mechanisms/types-of-campaign/airdrop
    pass


if __name__ == "__main__":
    # https://etherscan.io/token/0x89bb794097234e5e930446c0cec0ea66b35d7570#balances
    print(
        get_user_shares(
            pool="0x89bb794097234e5e930446c0cec0ea66b35d7570", block=21378029
        )
    )
