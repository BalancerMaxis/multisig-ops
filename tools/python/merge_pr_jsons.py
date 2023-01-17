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
    api_url = f'https://api.github.com/repos/{"GITHUB_REPO"}/multisig-ops/pulls/{"PR_NUMBER"}/files'
    URL = urlopen(api_url)
    pr_file_data = json.lods(URL.read())

    if debug:
        print(pr_file_data)

    # Get the list of modified and added files
    changed_files = []
    for file_json in pr_file_data:
        changed_files.append(file_json['filename]'])

    # Filter the list of added files for json files
    json_files = [filename for filename in changed_files if filename.endswith(".json")]

    # Extract the relevant information from the JSON file
    for json_file in json_files:
        if debug:
            print(f"Processing ${json_file}")
        # Get the JSON file from the repository
        with open(json_file, "r") as json_file:
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
