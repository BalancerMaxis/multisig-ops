from bal_addresses import AddrBook, BalPermissions, MultipleMatchesError, NoResultError
from brownie import network, accounts, Contract
import os


CHAINS_TO_KEEP = [
    #    "zkevm-main", # currently running in defender due to rpc issues
    "gnosis-main",
    "mode-main",
    "linea-main",
    "fraxtal-main",
]


def main():
    ## LOAD wallet
    errors = False
    mnemonic = os.environ["KEYWORDS"]
    account = accounts.from_mnemonic(mnemonic)
    print(f"Keeper Address: {account.address}")
    for chain in CHAINS_TO_KEEP:
        try:
            network.disconnect()
        except:
            pass
        try:
            network.connect(chain)
        except:
            print(f"Skipping {chain} because no network can be found")
            continue
        try:
            book = AddrBook(chain.replace("-main", ""))
        except:
            print(
                f"Skipping {chain} because no Address Information can be found in bal_addresses"
            )
            continue
        to_poke = []
        try:
            to_poke += book.extras.maxiKeepers.gaugeRewardsInjectors.values()
        except:
            print(f"no gaugeRewardsInjectors found in {chain}")
        try:
            to_poke += book.extras.maxiKeepers.gasStation
        except:
            print(f"no gasStation found in {chain}")
        for address in to_poke:
            try:
                c = Contract(address)
            except Exception as e:
                print(
                    f"WARNING: {chain}:{address}: failed to import contract (maybe scanner issues)?  {e}"
                )
                errors = True
                continue
            (ready, performdata) = c.checkUpkeep(b"")
            if ready:
                try:
                    c.performUpkeep(performdata, {"from": account})
                except Exception as e:
                    print(
                        f"WARNING: {chain}: {c.address}({book.reversebook.get(c.address)}) failed: {e}"
                    )
                    errors = True
            else:
                print(
                    f"{chain}: {c.address}({book.reversebook.get(c.address)}) not ready"
                )
    if errors:
        raise Exception("Some transactions failed")


if __name__ == "__main__":
    main()
