import json

import requests
import pandas as pd


def main(date="2024-01-05"):
    """
    map prop hashes in the payload with their pool id via the hidden hand api
    dump csv with pool id and usd amount
    this can then be crossrefd with the gsheet pool ids and amounts
    """
    r = requests.get("https://api.hiddenhand.finance/proposal/balancer")
    r.raise_for_status()

    # TODO: cant crossref with the csv because the csv is missing the pool id
    # df = pd.read_csv(f"../../../Bribs/{date}.csv")

    with open(f"../../../BIPs/00corePools/{date}.json", "r") as f:
        payload = json.load(f)
    result = []
    for transfer in payload["transactions"]:
        if "contractInputsValues" in transfer:
            if "_proposal" in transfer["contractInputsValues"]:
                for proposal in r.json()["data"]:
                    if (
                        proposal["proposalHash"]
                        == transfer["contractInputsValues"]["_proposal"]
                    ):
                        bribe = int(transfer["contractInputsValues"]["_amount"]) / 1e6
                        result.append({"pool_id": proposal["poolId"], "bribe": bribe})
    df = pd.DataFrame(result).set_index("pool_id").groupby("pool_id").sum()
    df.to_csv(f"../../../Bribs/{date}_review.csv")
    print(df.to_markdown())
    print(df["bribe"].sum())


if __name__ == "__main__":
    main()
