import json
import os
from json import JSONDecodeError

import requests

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def get_changed_files() -> list[dict]:
    github_repo = "BalancerMaxis/multisig-ops"
    # github_repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = 233
    # pr_number = os.environ["PR_NUMBER"]
    api_url = f'https://api.github.com/repos/{github_repo}/pulls/{pr_number}/files'
    response = requests.get(api_url)
    pr_file_data = json.loads(response.text)
    changed_files = []
    for file_json in pr_file_data:
        filename = (file_json['filename'])
        if "BIPs/" in filename and filename.endswith(".json"):
            # Check if file exists first
            if os.path.isfile(f"{ROOT_DIR}/{filename}") is False:
                print(f"{filename} does not exist")
                continue
            # Validate that file is a valid json
            with open(f"{ROOT_DIR}/{filename}", "r") as json_data:
                try:
                    payload = json.load(json_data)
                except JSONDecodeError:
                    print(f"{filename} is not proper json")
                    continue
                if isinstance(payload, dict) is False:
                    print(f"{filename} json is not a dict")
                    continue
                if "transactions" not in payload.keys():
                    print(f"{filename} json deos not contain a list of transactions")
                    continue
            changed_files.append(payload)
    return changed_files
