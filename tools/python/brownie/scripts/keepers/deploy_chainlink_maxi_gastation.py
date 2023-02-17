from brownie import GasStationExact, accounts, chain, network, Contract

from helpers.addresses import r

from great_ape_safe import GreatApeSafe

deployer_label="tmdelegate"
topup_amount = int(0.2*(10**18))
min_balance = int(0.4*(10**18))
admin_address = r.balancer.multisigs.maxi_ops


deployer = accounts[0] if not deployer_label else accounts.load(deployer_label)

def deploy(deployer_label="tmdelegate"):
    on_live_network = not "-fork" in network.show_active()
    GasStationExact.deploy(
       r.chainlink.keeper_registry,
       60 * 60,
       {"from": deployer},
       publish_source=on_live_network,
    )

def configure(address):
    signers = list(r.balancer.signers.maxis.values())
    num_signers = len(list(r.balancer.signers.maxis.values()))
    gas_station = Contract(address)
    gas_station.setWatchList(signers, [min_balance] * num_signers, [topup_amount] * num_signers, {"from": deployer.address})
    gas_station.transferOwnership(r.balancer.multisigs.maxi_ops, {"from": deployer.address})
    # Configure safe and replace gas_station
    safe = GreatApeSafe(admin_address)
    safe.init_chainlink()
    gas_station = safe.contract(gas_station.address)
    # Register
    safe.chainlink.register_upkeep(name="Maxi Gas Station",
                                   contract_addr=gas_station.address,
                                   gas_limit=500000,
                                   link_mantissa=int(5*(10**18)))
    safe.post_safe_tx(gen_tenderly=False)



