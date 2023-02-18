from brownie import GasStationExact, accounts, chain, network, Contract

from helpers.addresses import r

from great_ape_safe import GreatApeSafe

deployer_label="tmdelegate"
min_topup_amount = int(0.2*(10**18))
min_balance = int(0.5*(10**18))
admin_address = r.balancer.multisigs.maxi_ops
signers = list(r.balancer.deployers.values())

deployer = accounts[0] if not deployer_label else accounts.load(deployer_label)

def deploy(deployer_label="tmdelegate"):
    on_live_network = not "-fork" in network.show_active()
    GasStationExact.deploy(
       r.chainlink.keeper_registry,
       60 * 60 * 4, #don't send more than once every for hours for security
       {"from": deployer},
       publish_source=on_live_network,
    )


def transfer_owner(gas_station, owner):
    gas_station = Contract(gas_station)
    gas_station.transferOwnership(owner, {"from": deployer.address})

def configure(address):
    safe = GreatApeSafe(admin_address)
    num_signers = len(signers)
    # Configure safe and replace gas_station
    safe = GreatApeSafe(admin_address)
    safe.init_chainlink()
    gas_station = safe.contract(r.balancer.maxi_gas_station)
    gas_station.acceptOwnership()
    gas_station.setWatchList(signers, [min_balance] * num_signers, [min_topup_amount] * num_signers, {"from": deployer.address})
    # Register
    safe.chainlink.register_upkeep(name="Maxi Gas Station",
                                   contract_addr=gas_station.address,
                                   gas_limit=120000,
                                   link_mantissa=int(5*(10**18)))
    safe.post_safe_tx(gen_tenderly=False)

def update_watchlist(address):
    safe = GreatApeSafe(admin_address)
    num_signers = len(signers)
    gas_station = safe.contract(address)
    gas_station.setWatchList(signers, [min_balance] * num_signers, [min_topup_amount] * num_signers)
    safe.post_safe_tx(gen_tenderly=False, replace_nonce=79)
