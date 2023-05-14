import os
import sys
import json
from datetime import datetime
from urllib.request import urlopen

debug = True

base_json =  json.loads('''
{
  "version": "1.0",
  "chainId": "",
  "createdAt": 1675891944772,
  "meta": {
    "name": "Transactions Batch",
    "description": "",
    "txBuilderVersion": "1.13.2",
    "createdFromSafeAddress": "",
    "createdFromOwnerAddress": ""
  },
  "transactions": [
  ]
}
''')

def main():
    changed_files = sys.argv[1].split()
    date = datetime.utcnow()
    # Filter the list of added files for json files
    json_files = [filename for filename in changed_files if filename.endswith(".json") and "BIPs/BIP" in filename]
    txmap = {}
    # Extract the relevant information from the JSON file
    for json_file in json_files:
        if debug:
            print(f"Processing {json_file}")
        # Get the JSON file from the repository
        with open(json_file, "r") as json_data:
            data = json.load(json_data)
        # Extract the relevant information from the JSON file
        chain_id = data["chainId"]
        if chain_id not in txmap.keys():
            txmap[chain_id]={}
        safe = data["meta"]["createdFromSafeAddress"]
        print(safe)
        if safe not in txmap[chain_id].keys():
            txmap[chain_id][safe] = []
        txmap[chain_id][safe] = [*txmap[chain_id][safe], *data["transactions"]]
        print(txmap)

    # Create the directory name.  %W is week of year, week starts on monday
    dir_name = f"00batched/{date.year}-{date.strftime('%U')}"
    # Create the directory if it does not exist
    if not os.path.exists(f"BIPs/{dir_name}"):
        os.mkdir(f"BIPs/{dir_name}")

    # Generate the files
    for chain, safes in txmap.items():
        for safe, txlist in safes.items():
            result = base_json
            result["transactions"] = txlist
            file_name = f"{chain_id}-{safe}.json"
            with open(f"BIPs/{dir_name}/{file_name}", "w") as new_file:
                json.dump(result, new_file, indent=2)


if __name__ == "__main__":
    main()
