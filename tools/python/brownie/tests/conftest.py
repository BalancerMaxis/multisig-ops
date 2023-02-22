import pytest
import time
from brownie import (
    interface,
    accounts,
    periodicRewardsInjector,
    testToken,

)
from dotmap import DotMap
import pytest

##  Accounts
STREAMER_ADDRESS = "0x48B024C6620b62Ea65cD10914801ce062b436Bb5"
STREAMER_OWNER_ADDRESS = "0x0F3e0c4218b7b0108a3643cFe9D3ec0d4F57c54e" ## authorizer-adaptor
ARBI_WSTETH_USDC_WHALE = "0x78c5bdf04d088766dd70ef5258a8c272ea155594"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"





@pytest.fixture()
def get_rewards():
    return "0x1afe22a6"  # get_rewards has function selector "0x1afe22a6"

@pytest.fixture()
def admin():
    return accounts[1]



@pytest.fixture()
def whale():
    return ARBI_WSTETH_USDC_WHALE


@pytest.fixture()
def gauge(streamer):
    return interface.IRewardsOnlyGauge(streamer.reward_receiver())

@pytest.fixture()
def authorizer_adaptor():
    return STREAMER_OWNER_ADDRESS


@pytest.fixture()
def streamer():
    return interface.IChildChainStreamer(STREAMER_ADDRESS)



@pytest.fixture()
def upkeep_caller():
    return accounts[2]


@pytest.fixture()
def deployer():
    return accounts[0]


@pytest.fixture()
def injector(deploy):
    return deploy.injector


@pytest.fixture()
def token(deploy):
    return deploy.token


@pytest.fixture()
def deploy(deployer, admin, upkeep_caller, authorizer_adaptor, streamer, gauge, get_rewards):
    """
    Deploys, vault and test strategy, mock token and wires them up.
    """

    token = testToken.deploy(admin, 100000, {"from": deployer})

    injector = periodicRewardsInjector.deploy(
        upkeep_caller,
        60*5, #minWaitPeriodSeconds
        token.address,
        {"from": deployer}
    )
    print(token.balanceOf(deployer))
    injector.transferOwnership(admin, {"from": deployer})
    token.transfer(injector.address, 100000, {"from": admin})
    injector.acceptOwnership({"from": admin})
    # def add_reward(_token: address, _distributor: address, _duration: uint256)
    streamer.add_reward(token, authorizer_adaptor, 60*60, {"from": authorizer_adaptor})
    tokens = 8*[ZERO_ADDRESS]
    for i in range(0,7,1):
        if gauge.reward_tokens(i) == ZERO_ADDRESS:
            print(f"Found Zero address at position {i}")
        else:
            tokens[i]=gauge.reward_tokens(i)

    print(f"i is {i}")
    tokens[i] = token.address
    print(f"reward_tokens(i+1)={gauge.reward_tokens}")
    gauge.set_rewards(streamer, get_rewards, tokens, {"from": authorizer_adaptor})

    return DotMap(
        injector=injector,
        token=token,
    )


