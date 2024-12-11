from bal_tools import Subgraph

# https://docs.merkl.xyz/merkl-mechanisms/types-of-campaign/airdrop
if __name__ == "__main__":

    def get_user_shares(pool="0xd1d7fa8871d84d0e77020fc28b7cd5718c446522"):
        query = """{
            query PoolShares($where: PoolShare_filter, $block: Block_height) {
                poolShares(where: $where, block: $block) {
                    user {
                        id
                        shares {
                            balance
                        }
                    }
                }
            }
        }"""
        params = {
            "where": {
                "balance_gt": 0.001,
                "pool_in": [pool],
            },
            "block": {"number": 37435326},
        }
        return Subgraph().fetch_graphql_data("apiv3", query, params)

    print(get_user_shares())
