from bal_addresses import AddrBook
from collections import defaultdict
import csv
from bal_addresses import AddrBook
import json
import copy


TX_BUILDER_GLOBAL_JSON = json.loads(
'''{
  "version": "1.0",
  "chainId": "1",
  "createdAt": 1688559620808,
  "meta": {
    "name": "Transactions Batch",
    "description": "disableRecoveryMode Safu Pools",
    "txBuilderVersion": "1.16.0",
    "createdFromSafeAddress": "",
    "createdFromOwnerAddress": ""
  }
}
''')


TX_BUILDER_TX_JSON = json.loads(
'''    {
      "to": "",
      "value": "0",
      "data": null,
      "contractMethod": {
        "inputs": [],
        "name": "disableRecoveryMode",
        "payable": false
      },
      "contractInputsValues": null
    }

''')

CHAIN_NAMES_BY_ID =  {str(v): k for k, v in AddrBook.CHAIN_IDS_BY_NAME.iteritems()}
csv_file = "../../BIPs/00notGov/07-2023-disableRecovery/readyPools.csv"
def main():
    pool_csv = list(csv.DictReader(open(csv_file)))
    txlist_by_chain = defaultdict(list)
    ## Parse briibes per platform
    for poolinfo in pool_csv:
        pool_id = poolinfo["current pool ID"]
        chain_id = str(poolinfo["Network"])
        pool_address = pool_id[:42]  ## first 42 characters of pool ID is address
        tx = copy.copy(TX_BUILDER_TX_JSON)
        tx["to"] = pool_address
        txlist_by_chain[chain_id].append(tx)
    print (txlist_by_chain["137"])
    for chain_id, txlist in txlist_by_chain.items():
        chain_name = CHAIN_NAMES_BY_ID.get(chain_id)
        print(f"Processing: {chain_name}({chain_id})")
        book = AddrBook(chain_name)
        multisig = book.flatbook[book.search_unique("multisigs/emergency")]
        payload = TX_BUILDER_GLOBAL_JSON
        payload["chainId"] = chain_id
        payload["createdFromSafeAddress"] = multisig
        payload["transactions"] = txlist
        with open(f"../../BIPs/00notGov/07-2023-disableRecovery/{chain_id}-{multisig}.json", "w") as f:
            json.dump(payload, f, indent=2)

if __name__ == "__main__":
    main()
