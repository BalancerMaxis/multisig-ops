from bal_addresses import AddrBook, BalPermissions, MultipleMatchesError, NoResultError
from brownie import network, accounts, Contract
import os

def main():
    ## LOAD wallet
    mnemonic =  os.environ["KEYWORDS"]
    account = accounts.from_mnemonic(mnemonic)
    print(f"Keeper Address: {account.address}")
    ## ZKEVM
    network.disconnect()
    network.connect("zkevm-main")
    book = AddrBook("zkevm")
    injectors =  book.extras.maxiKeepers.gaugeRewardsInjectors.values()
    for injectorAddress in injectors:
        injector = Contract(injectorAddress)
        (ready, performdata) = injector.checkUpkeep(b"")
        if ready:
            injector.performUpkeep(performdata, {"from": account})
        else:
            print(f"{injector.address} not ready")

if __name__ == "__main__":
    main()