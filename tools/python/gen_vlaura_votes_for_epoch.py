from dune_client.client import DuneClient
from dune_client.types import QueryParameter
from dune_client.query import QueryBase


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


if __name__ == "__main__":
    # get all revenue data for a given epoch
    df = get_df_revenue()

    # dev: uncomment to use cached data in dev mode
    # df.to_csv("cache.csv", index=False)
    # df = pd.read_csv("cache.csv")

    # clean data
    df = df[df["protocol_fee_collected"] != "<nil>"]
    df["protocol_fee_collected"] = df["protocol_fee_collected"].astype(float)

    # filter out optimism
    df = df[df["blockchain"] != "optimism"]

    # get top 6 pools by revenue
    df = df.sort_values(by=["protocol_fee_collected"], ascending=False).head(6)

    # add column with share of total revenue
    total_revenue = df["protocol_fee_collected"].sum()
    df["share"] = df["protocol_fee_collected"] / total_revenue

    print(df.to_markdown(index=False))
