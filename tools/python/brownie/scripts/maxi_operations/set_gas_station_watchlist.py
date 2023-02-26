from great_ape_safe import GreatApeSafe
from web3 import Web3
from helpers.addresses import r


def main():
    addresses=[]
    topup_amounts=[]
    min_topups=[]
    safe = GreatApeSafe(r.balancer.multisigs.maxi_ops)
    signers = r.balancer.signers.maxis
    deployers = r.balancer.deployers

    for name,address in signers.items():
        if name in deployers.keys():
            # Deployers get more gas in the deployer but no signer gas
            addresses.append(deployers[name])
            topup_amounts.append(int(0.5*10**18))  # .5 ETH  topup for deployers
            min_topups.append(int(0.2*10**18))  # .2 ETH min topup = always has atleast .3
        else:
            # This person only has a signer address so gas them less
            addresses.append(address)
            topup_amounts.append(int(0.25*10**18)) # .25 eth for signers
            min_topups.append(int(0.15*10**18))  # always has at least 0.1

    gs = safe.contract(r.balancer.maxi_gas_station)
    gs.setWatchList(addresses, topup_amounts, min_topups)
    # adding 1 deployer and 3 signers requires a total of 1.25 eth to topup all new signers to from empty to full
    safe.post_safe_tx(gen_tenderly=False)
