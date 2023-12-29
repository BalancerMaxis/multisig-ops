import urllib.request


def get_subgraph_url(chain_name: str):
    # ref: https://github.com/BalancerMaxis/bal_addresses/blame/52910c55036a298b33228407a5b0d94a825414ca/gen_pools_and_gauges.py#L11-L28
    chain_name = "gnosis-chain" if chain_name == "gnosis" else chain_name
    frontend_file = f"https://raw.githubusercontent.com/balancer/frontend-v2/develop/src/lib/config/{chain_name}/index.ts"
    magic_word = "subgraph:"
    found_magic_word = False
    with urllib.request.urlopen(frontend_file) as f:
        for line in f:
            if found_magic_word:
                return line.decode("utf-8").strip().strip(" ,'")
            if magic_word + " " in str(line):
                # url is on same line
                return line.decode("utf-8").split(magic_word)[1].strip().strip(",'")
            if magic_word in str(line):
                # url is on next line, return it on the next iteration
                found_magic_word = True
