import os
import json
from datetime import datetime
from urllib.request import urlopen

date = datetime.utcnow()

debug = True;
def main():
    # Get the REPO_ROOT from the environment variable
    # Read the event payload
    pr_branch_root = f'{os.environ["GITHUB_WORKSPACE"]}/pr'
    main_branch_root = f'{os.environ["GITHUB_WORKSPACE"]}/main'
    github_repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    #"https://api.github.com/repos/${GITHUB_REPOSITORY}/pulls/${{ github.event.pull_request.number }}/files
    api_response = f'https://api.github.com/repos/{"GITHUB_REPO"}/multisig-ops/pulls/{"PR_NUMBER"}/files'
    with open(os.environ["GITHUB_EVENT_PATH"], "r") as event_file:
        event_data = json.load(event_file)
    if debug:
        print(event_data)

    # Get the list of modified and added files
    modified_files = event_data["pull_request"]["changed_files"]
    added_files = [item for item in modified_files if item["status"] == "added"]

    # Filter the list of added files for json files
    json_files = [item for item in added_files if item["filename"].endswith(".json")]

    # Extract the relevant information from the JSON file
    for json_file in json_files:
        # Get the JSON file from the repository
        with open(json_file["filename"], "r") as json_file:
            data = json.load(json_file)
        # Extract the relevant information from the JSON file
        chain_id = data["chainId"]
        created_from_safe_address = data["meta"]["createdFromSafeAddress"]
        transactions = data["transactions"]
        # Get the current date
        date = datetime.now()
        # Create the directory name
        dir_name = f"{date.year}-week{date.strftime('%N')}"
        # Create the directory if it does not exist
        if not os.path.exists(f"{main_branch_root}/BIPs/{dir_name}"):
            os.mkdir(f"{main_branch_root}/BIPs/{dir_name}")
        # Create the file name
        file_name = f"{chain_id}-{created_from_safe_address}"
        # Check if the file already exists
        if os.path.exists(f"{main_branch_root}/BIPs/{dir_name}/{file_name}"):
            # If the file exists, read the existing transactions
            with open(f"{main_branch_root}/BIPs/{dir_name}/{file_name}", "r") as existing_file:
                existing_data = json.load(existing_file)
                existing_transactions = existing_data["transactions"]
            # Add the new transactions to the existing transactions
            existing_data["transactions"].extend(existing_transactions)
        # Write the transactions to the file
            with open(f"{main_branch_root}/BIPs/{dir_name}/{file_name}", "w") as output_file:
                json.dump({"transactions": transactions}, output_file)
        # Otherwise seed the new multisig file with the entirety of the source json
        else:
            with open(f"{main_branch_root}/BIPs/{dir_name}/{file_name}", "r") as new_file:
                new_file.write(json.dumps(data))


if __name__ == "__main__":
    main()
