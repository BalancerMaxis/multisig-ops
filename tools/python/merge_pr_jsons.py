import os
import json
from datetime import datetime
from urllib.request import urlopen

debug = True


def main():

    date = datetime.utcnow()
    # Get the REPO_ROOT from the environment variable
    # Read the event payload
    pr_branch_root = f'{os.environ["GITHUB_WORKSPACE"]}/pr'
    main_branch_root = f'{os.environ["GITHUB_WORKSPACE"]}/main'
    if debug:
        print(f"main_branch_rooot: ${main_branch_root}\npr_branch_root:{pr_branch_root}")
    github_repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    api_url = f'https://api.github.com/repos/{github_repo}/pulls/{pr_number}/files'
    if debug:
        print(f"api url: {api_url}")
    url = urlopen(api_url)
    pr_file_data = json.loads(url.read())

    if debug:
        print(pr_file_data)

    # Get the list of modified and added files
    changed_files = []
    for file_json in pr_file_data:
        changed_files.append(file_json['filename'])
    if debug:
        print(f"Changed Files:{changed_files}")
    # Filter the list of added files for json files
    json_files = [filename for filename in changed_files if filename.endswith(".json")]

    # Extract the relevant information from the JSON file
    for json_file in json_files:
        if debug:
            print(f"Processing ${json_file}")
        # Get the JSON file from the repository
        with open(f"{pr_branch_root}/{json_file}", "r") as json_data:
            data = json.load(json_data)
        # Extract the relevant information from the JSON file
        chain_id = data["chainId"]
        created_from_safe_address = data["meta"]["createdFromSafeAddress"]
        transactions = data["transactions"]
        # Create the directory name.  %W is week of year, week starts on monday
        dir_name = f"00batched/{date.year}-{date.strftime('%U')}"
        # Create the directory if it does not exist
        if not os.path.exists(f"{main_branch_root}/BIPs/{dir_name}"):
            os.mkdir(f"{main_branch_root}/BIPs/{dir_name}")
        # Create the file name
        file_name = f"{chain_id}-{created_from_safe_address}.json"
        # Check if the file already exists
        if debug:
            print(f"output json file path is: {main_branch_root}/BIPs/{dir_name}/{file_name}")
        if os.path.exists(f"{main_branch_root}/BIPs/{dir_name}/{file_name}"):
            # If the file exists, read the existing transactions
            with open(f"{main_branch_root}/BIPs/{dir_name}/{file_name}", "r") as existing_file:
                existing_data = json.load(existing_file)
            # Add the new transactions to the existing transactions
            existing_data["transactions"].extend(transactions)
        # Write the new file
            if debug:
                print(f"transactions to add as part of ${json_file} are : \n {transactions}")
            with open(f"{main_branch_root}/BIPs/{dir_name}/{file_name}", "w") as output_file:
                json.dump(existing_data, output_file, indent=6)
        # Otherwise seed the new multisig file with the entirety of the source json
        else:
            with open(f"{main_branch_root}/BIPs/{dir_name}/{file_name}", "w") as new_file:
                json.dump(data, new_file, indent=6)


if __name__ == "__main__":
    main()
