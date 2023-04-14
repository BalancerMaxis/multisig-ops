from brownie import Contract
from eth_abi import encode_abi
import json


multisig = "0x4D6175d58C5AceEf30F546C0d5A557efFa53A950"
bbeusd= Contract("0x50Cf90B954958480b8DF7958A9E965752F627124")
vault = Contract("0xBA12222222228d8Ba445958a75a0704d566BF2C8")
bbeusdId = "0x50cf90b954958480b8df7958a9e965752f62712400000000000000000000046f"
exitKind = 255 # RecoveryMode Exit

## What we want to get out
recoveryTokens = ["0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "0xdAC17F958D2ee523a2206206994597C13D831ec7", "0x6B175474E89094C44Da98b954EedeAC495271d0F"]

## initial balances

pool = bbeusd
poolId = bbeusdId
types = ["uint8", "uint256"]

(pooltokens, amounts, whocares) = vault.getPoolTokens(poolId)
tokens = {}

txs = []
## WD top level tokens
for token in pooltokens:
    tokens[token] = Contract(token)

encoded = encode_abi(types, [255, bbeusd.balanceOf(multisig)])
txs.append(vault.exitPool(bbeusdId, multisig, multisig, (pooltokens, [0,0,0,0], encoded.hex(), False), {'from': multisig}))

## wd from linear pool tokens
for token in tokens.values():
    if token.address == bbeusd.address:
        poolId = bbeusdId
    else:
        poolId = token.getPoolId()
    print (f"processing {token.name()} at {token.address}")
    encoded = encode_abi(types, [255, token.balanceOf(multisig)])
    (lineartokens, yyy, zzz) = vault.getPoolTokens(poolId)

    if token != pool:
        txs.append(vault.exitPool(poolId, multisig, multisig, (lineartokens, [0,0,0], encoded.hex(), True), {'from': multisig}))

## wd from vault
oplist = []
for token in recoveryTokens:
    amount = vault.getInternalBalance(multisig, [token])[0]
    oplist.append((1, token, amount, multisig, multisig))

txs.append(vault.manageUserBalance(oplist, {'from': multisig}))

### Generate multisig payload
with open("txbuilder_calldata.json", "r") as f:
    endjson = json.load(f)

endjson["meta"]["createdFromSafeAddress"] = multisig
txtemplate = endjson["transactions"][0]
txlist = []

# Pack all the input data from our txs into txjson format
for tx in txs:
    j = txtemplate
    j["data"] = tx.input
    txlist.append(j)

txtemplate = endjson["transactions"] = txlist

with open("eulerBreakoutOutput.json", "w") as f:
    json.dump(endjson, f)
