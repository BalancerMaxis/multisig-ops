from brownie import accounts, Contract
import json

operating_account = accounts[0]
dolaPoolAddress = "0x133d241F225750D2c92948E464A5a80111920331"
BalancerDAOmultisig = "0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f"

with open("./IComposableStable.json", "r") as f:
    poolAbi = json.load(f)


dolapool = Contract.from_abi("ComposableStablePool", dolaPoolAddress, poolAbi)
authorizer = Contract.from_explorer("0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6")
vault = Contract.from_explorer("0xba12222222228d8ba445958a75a0704d566bf2c8")
RolesToAllow = [
    dolapool.getActionId(dolapool.pause.signature),
    dolapool.getActionId(dolapool.unpause.signature),
]
authorizer.grantRoles(RolesToAllow, operating_account, {"from": BalancerDAOmultisig})
dolapool.unpause({"from": operating_account})
### Do some stuff here
dolapool.pause({"from": operating_account})
