from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from web3 import Web3

gauges_to_remove = {
    "POLY: Balancer 20USDC-40TEL-40DFX RewardGauge Deposit":   "0xb61014De55A7AB12e53C285d88706dca2A1B7625",
    "Balancer NWWP Gauge Deposit (NOTE/WETH 50/50)":   "0x96d7e549eA1d810725e4Cd1f51ed6b4AE8496338",
    "Balancer 50N/A-50N/A Gauge Deposit (D2D/BAL 50/50)":   "0xf46FD013Acc2c6988BB2f773bd879101eB5d4573",
    "Balancer 20DAI-80TCR Gauge Deposit":   "0xAde9C0054f051f5051c4751563C7364765Bf52f5",
    "Balancer 20WETH-80HAUS Gauge Deposit":   "0x00Ab79a3bE3AacDD6f85C623f63222A07d3463DB",
    "ARBI: Balancer B-80PICKLE-20WETH RewardGauge Deposit":   "0x231B05F3a92d578EFf772f2Ddf6DacFFB3609749",
    "ARBI: Balancer 20WETH-80CRE8R RewardGauge Deposit":   "0x077794c30AFECcdF5ad2Abc0588E8CEE7197b71a",
    "POLY: Balancer TELX-60TEL-20BAL-20USDC RewardGauge Deposit":   "0x7C56371077fa0dD8327E5C53Ee26a37D14b671ad",
    "POLY: Balancer TELX-50TEL-50BAL RewardGauge Deposit":   "0xe0779Dc81B5DF4D421044f7f7227f7e2F5b0F0cC",
    ## The one below is already disabled and is a test
    "ARBI: Balancer 80MAGIC-20WETH RewardGauge Deposit": "0x785F08fB77ec934c01736E30546f87B4daccBe50",
}

def main():
    safe = GreatApeSafe(registry.eth.balancer.multisigs.dao)
    authorizer = safe.contract(registry.eth.balancer.authorizer_adapter)
    killGauge = Web3.sha3(text="killGauge()")[0:4]

    for name, address in gauges_to_remove.items():
        gauge = safe.contract(address)
        print(f"isKilled on gauge {name} at {gauge.address}  = {bool(gauge.is_killed())}")
        if(gauge.is_killed):
            continue
        print (f"Killing {address} with name ${name}")
        authorizer.performAction(address, killGauge)
        print(f"isKilled on gauge {name} at {gauge.address}  is now {gauge.is_killed()}")

    safe.post_safe_tx(call_trace=True, gen_tenderly=False)

