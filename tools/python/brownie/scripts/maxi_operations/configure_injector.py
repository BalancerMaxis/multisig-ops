from brownie import interface, chain
import json
from helpers.addresses import r

## https://docs.chain.link/chainlink-automation/supported-networks/#configurations
REGISTRY_BY_CHAIN = {
    42161: "0x75c0530885F385721fddA23C539AF3701d6183D4",
    137: "0x02777053d6764996e594c3E88AF1D58D5363a2e6",
}

REGISTRAR_BY_CHAIN = {
    42161: "0x4F3AF332A30973106Fe146Af0B4220bBBeA748eC",
    137: "0xDb8e8e2ccb5C033938736aa89Fe4fa1eDfD15a1d",
}

LINK_BY_CHAIN = {
    42161: "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4",
    137: "0xb0897686c545045aFc77CF20eC7A532E3120E0F1"
}

REGISTER_CHAINLINK_TEMPLATE = '''
{
  "version": "1.0",
  "chainId": "42161",
  "createdAt": 1680004312316,
  "meta": {
    "name": "Transactions Batch",
    "description": "",
    "txBuilderVersion": "1.13.3",
    "createdFromSafeAddress": "",
    "createdFromOwnerAddress": "",
    "checksum": ""
  },
  "transactions": [
    {
      "to": "0x0000000000000000000000000000000000000000",
      "value": "0",
      "data": null,
      "contractMethod": {
        "inputs": [
          {
            "internalType": "address",
            "name": "_to",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "_value",
            "type": "uint256"
          },
          {
            "internalType": "bytes",
            "name": "_data",
            "type": "bytes"
          }
        ],
        "name": "transferAndCall",
        "payable": false
      },
      "contractInputsValues": {
        "_to": "0x0000000000000000000000000000000000000000",
        "_value": "0",
        "_data": "0x"
      }
    }
  ]
}
'''

CONF_WATCHLIST_TEMPLATE = '''
{
  "version": "1.0",
  "chainId": "42161",
  "createdAt": 1680004312316,
  "meta": {
    "name": "Transactions Batch",
    "description": "",
    "txBuilderVersion": "1.13.3",
    "createdFromSafeAddress": "0xc38c5f97B34E175FFd35407fc91a937300E33860",
    "createdFromOwnerAddress": "",
    "checksum": "0xc9ee3323e8dd9c717480579e569a38c8396a5b86b21b97a044912b993636afb1"
  },
  "transactions": [
    {
      "to": "0x0000000000000000000000000000000000000000",
      "value": "0",
      "data": null,
      "contractMethod": {
        "inputs": [
          {
            "internalType": "address[]",
            "name": "streamerAddresses",
            "type": "address[]"
          },
          {
            "internalType": "uint256[]",
            "name": "amountsPerPeriod",
            "type": "uint256[]"
          },
          {
            "internalType": "uint8[]",
            "name": "maxPeriods",
            "type": "uint8[]"
          }
        ],
        "name": "setRecipientList",
        "payable": false
      },
      "contractInputsValues": {
        "streamerAddresses": "[0x0000000000000000000000000000000000000000]",
        "amountsPerPeriod": "[1]",
        "maxPeriods": "[1]"
      }
    },
    {
      "to": "0x0000000000000000000000000000000000000000",
      "value": "0",
      "data": null,
      "contractMethod": {
        "inputs": [
          {
            "internalType": "address",
            "name": "recipient",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
          }
        ],
        "name": "transfer",
        "payable": false
      },
      "contractInputsValues": {
        "recipient": "0x0000000000000000000000000000000000000000",
        "amount": "1"
      }
    }
  ]
}
'''

ACCEPT_OWNERSHIP_TEMPLATE = '''
{
  "version": "1.0",
  "chainId": "42161",
  "createdAt": 1680004312316,
  "meta": {
    "name": "Transactions Batch",
    "description": "",
    "txBuilderVersion": "1.13.3",
    "createdFromSafeAddress": "0xc38c5f97B34E175FFd35407fc91a937300E33860",
    "createdFromOwnerAddress": "",
    "checksum": "0xc9ee3323e8dd9c717480579e569a38c8396a5b86b21b97a044912b993636afb1"
  },
  "transactions": [
    {
      "to": "0x2F1901f2A82fcC3Ee9010b809938816B3b06FA6A",
      "value": "0",
      "data": null,
      "contractMethod": {
        "inputs": [],
        "name": "acceptOwnership",
        "payable": false
      },
      "contractInputsValues": null
    }
  ]
}
'''


def register_upkeep(upkeep_contract,
                                        name,
                                        gas_limit,
                                        link_deposit_gwei,
                                        sender,
                                        chain_id=chain.id,
                                        calldata=b"",
                                        source=69,
                                        ):

    registrar = interface.IKeeperRegistrar(REGISTRAR_BY_CHAIN[chain_id])
    link_address = LINK_BY_CHAIN[chain_id]
    calldata = registrar.register.encode_input(
                name,  # string memory name,
                b"",  # bytes calldata encryptedEmail,
                upkeep_contract,  # address upkeepContract,
                gas_limit,  # uint32 gasLimit,
                sender,  # address adminAddress,
                calldata,  # bytes calldata checkData,
                link_deposit_gwei,  # uint96 amount,
                source,  # source (uint8)
                sender,  # address sender
    )
    payload = json.loads(REGISTER_CHAINLINK_TEMPLATE)
    payload["chainId"] = chain_id
    payload["meta"]["createdFromSafeAddress"] = sender
    payload["transactions"][0]["to"] = link_address
    payload["transactions"][0]["contractInputsValues"]["_to"] = registrar.address
    payload["transactions"][0]["contractInputsValues"]["_value"] = link_deposit_gwei
    payload["transactions"][0]["contractInputsValues"]["_data"] = calldata
    return json.dumps(payload)


def set_recipient_list(streamer_addresses, amounts_per_period, max_periods, injector_address, safe_address, token_address, chain_id=chain.id):
    payload = json.loads(CONF_WATCHLIST_TEMPLATE)
    payload["chainId"] = chain_id
    payload["meta"]["createdFromSafeAddress"] = safe_address
    payload["transactions"][0]["to"] = injector_address
    payload["transactions"][0]["contractInputsValues"]["streamerAddresses"] = streamer_addresses
    payload["transactions"][0]["contractInputsValues"]["amountsPerPeriod"] = amounts_per_period
    payload["transactions"][0]["contractInputsValues"]["maxPeriods"] = max_periods
    ### Send coins
    total=0
    for i in range(0, len(amounts_per_period), 1):
        total += amounts_per_period[i] * max_periods[i]
    payload["transactions"][1]["to"] = token_address
    payload["transactions"][1]["contractInputsValues"]["recipient"] = injector_address
    payload["transactions"][1]["contractInputsValues"]["amount"] = total
    return json.dumps(payload)


def accept_ownership(injector_address, safe_address, chain_id=chain.id):
    payload = json.loads(CONF_WATCHLIST_TEMPLATE)
    payload["chainId"] = chain_id
    payload["meta"]["createdFromSafeAddress"] = safe_address
    payload["transactions"][0]["to"] = injector_address
    return json.dumps(payload)
