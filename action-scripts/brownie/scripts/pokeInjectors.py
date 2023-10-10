from bal_addresses import AddrBook, BalPermissions, MultipleMatchesError, NoResultError
from brownie import network, accounts, Contract
import os

## LOAD wallet
mnemonic =  os.environ["GITHUB_REPOSITORY"]
account = accounts.from_mnemonic(mnemonic)
print(f"Keeper Address: {account.address}")
## ZKEVM
network.disconnect()
network.connect("zkevm-main")
book = AddrBook("zkvem")
injectors =  book.extras.maxiKeepers.gaugeRewardsInjectors.values()
for injectorAddress in injectors:
    injector = Contract(injectorAddress)
    (ready, performdata) = injector.checkUpkeep(b"")
    if ready:
        injector.performUpkeep(performdata, {"from": account})

