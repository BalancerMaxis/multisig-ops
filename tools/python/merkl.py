import json
from datetime import datetime

import requests

BASE_URL = "https://api.merkl.xyz/"
MERKL_DISTRIBUTOR = "0x3Ef3D8bA38EBe18DB133cEc108f4D14CE00Dd9Ae"


def claim_merkl(chain_id, user):
    """
    build safe payload for claiming rewards from merkl
    ref: https://docs.merkl.xyz/integrate-merkl/integrate-merkl#v3-userrewards
    """
    url = f"{BASE_URL}/v3/userRewards?"
    params = {"user": user, "chainId": chain_id, "proof": True}
    r = requests.get(url, params=params)
    try:
        r.raise_for_status()
    except:
        print(r.json())
    result = r.json()
    claim = {"user": [], "tokens": [], "amounts": [], "proofs": []}
    for token in result:
        claim["user"].append(user)
        claim["tokens"].append(token)
        claim["amounts"].append(result[token]["accumulated"])
        claim["proofs"].append(result[token]["proof"])

    if len(claim["user"]) > 0:
        payload = {
            "chainId": str(chain_id),
            "createdAt": int(datetime.timestamp(datetime.now())),
            "meta": {
                "name": "Transactions Batch",
                "description": "Claim all earned rewards from Merkl",
                "createdFromSafeAddress": str(user),
            },
            "transactions": [
                {
                    "to": MERKL_DISTRIBUTOR,
                    "value": "0",
                    "data": None,
                    "contractMethod": {
                        "inputs": [
                            {
                                "internalType": "address[]",
                                "name": "users",
                                "type": "address[]",
                            },
                            {
                                "internalType": "address[]",
                                "name": "tokens",
                                "type": "address[]",
                            },
                            {
                                "internalType": "uint256[]",
                                "name": "amounts",
                                "type": "uint256[]",
                            },
                            {
                                "internalType": "bytes32[][]",
                                "name": "proofs",
                                "type": "bytes32[][]",
                            },
                        ],
                        "name": "claim",
                        "payable": False,
                    },
                    "contractInputsValues": {
                        "users": str(claim["user"]),
                        "tokens": str(claim["tokens"]),
                        "amounts": str(claim["amounts"]),
                        "proofs": str(claim["proofs"]),
                    },
                }
            ],
        }
    else:
        return
    return payload


if __name__ == "__main__":
    chain = 1
    user = "0x529619a10129396a2F642cae32099C1eA7FA2834"
    payload = claim_merkl(chain, user)
    with open(
        f"../../MaxiOps/merkl/{payload['createdAt']}-{chain}-{user}.json",
        "w",
    ) as f:
        json.dump(payload, f, indent=2)
