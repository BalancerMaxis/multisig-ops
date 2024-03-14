
def add_last_join_exit(incentives: Dict[str, Dict], chain: Chains, alertTimeStamp: Optional[int] = None) -> Dict[str, Dict]:
    """
    adds last_join_exit for each pool in the incentives list for reporting.
    Returns the same thing as inputed with the additional field added for each line
    """
    q = Subgraph(chain.value)
    for pool_id, incentive_data in incentives.items():
        try:
            timestamp = q.get_last_join_exit(pool_id)
        except:
            incentive_data["last_join_exit"] = "Error fetching"
            continue
        gmt_time = datetime.datetime.utcfromtimestamp(timestamp)
        human_time = gmt_time.strftime('%Y-%m-%d %H:%M:%S GMT')
        if alertTimeStamp and timestamp < alertTimeStamp:
            human_time = f"!!!{human_time}"
        incentive_data["last_join_exit"] = human_time
    return incentives
