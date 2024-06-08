import requests
import json
import argparse

from bal_addresses import AddrBook
from dotenv import load_dotenv
load_dotenv()


flatbook = AddrBook("mainnet").flatbook
vlaura_safe_addr = flatbook["multisigs/vote_incentive_recycling"]
sign_msg_lib_addr = flatbook["gnosis/sign_message_lib"]

REPORT_DIR = f"../../../MaxiOps/vlaura_voting"

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vote processing script")
    parser.add_argument(
        "--vote-day",
        type=str,
        help="Date that votes are are being posted. should be YYYY-MM-DD",
    )
    args = parser.parse_args()

    with open(f"{REPORT_DIR}/{args.vote_day}-payload.json", "r") as f:
        payload = json.load(f)

    response = requests.post(
            "https://seq.snapshot.org/",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Referer": "https://snapshot.org/",
            },
            data=json.dumps(
                {
                    "address": vlaura_safe_addr,
                    "data": payload,
                    "sig": "0x",
                }
            ),
        )

    if response.ok:
        print("Successfully posted to the vote relayer API.")
        print(response.json())
    else:
        print("Failed to post to the vote relayer API.")
        print(response.text)