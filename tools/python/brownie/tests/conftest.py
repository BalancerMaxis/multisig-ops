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
ARBI_LDO_WHALE = "0x25ab7dc4ddcacb6fe75694904db27602175245f1"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ARBI_LDO_ADDRESS = "0x13Ad51ed4F1B7e9Dc168d8a00cB3f4dDD85EfA60"
WEEKLY_INCENTIVE = 200*10**18
STREAMER_STUCK = 6003155 ## Something that seems stuck in the streamer LDO



@pytest.fixture(scope="module")
def get_rewards():
    return "0x1afe22a6"  # get_rewards has function selector "0x1afe22a6"


@pytest.fixture(scope="module")
def admin():
    return accounts[1]



@pytest.fixture(scope="module")
def whale():
    return ARBI_WSTETH_USDC_WHALE


@pytest.fixture(scope="module")
def gauge(streamer):
    return interface.IRewardsOnlyGauge(streamer.reward_receiver())

@pytest.fixture(scope="module")
def authorizer_adaptor():
    return STREAMER_OWNER_ADDRESS


@pytest.fixture(scope="module")
def streamer():
    return interface.IChildChainStreamer(STREAMER_ADDRESS)



@pytest.fixture(scope="module")
def upkeep_caller():
    return accounts[2]

@pytest.fixture()
def weekly_incentive():
    return WEEKLY_INCENTIVE
@pytest.fixture(scope="module")
def deployer():
    return accounts[0]


@pytest.fixture()
def injector(deploy):
    return deploy.injector


@pytest.fixture(scope="module")
def token():
    return interface.IERC20(ARBI_LDO_ADDRESS)


@pytest.fixture(scope="module")
def deploy(deployer, admin, upkeep_caller, authorizer_adaptor, streamer, gauge, get_rewards, token):
    """
    Deploys, vault and test strategy, mock token and wires them up.
    """

    token.transfer(admin, 1000*10**18, {"from": ARBI_LDO_WHALE})

    injector = periodicRewardsInjector.deploy(
        upkeep_caller,
        60*5, #minWaitPeriodSeconds
        token.address,
        {"from": deployer}
    )
    print(token.balanceOf(deployer))
    injector.transferOwnership(admin, {"from": deployer})
    token.transfer(injector.address, 500*10**18, {"from": admin})
    injector.acceptOwnership({"from": admin})

    return DotMap(
        injector=injector,
        token=token,
    )


