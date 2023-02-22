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

STREAMER_ADDRESS = "0x48B024C6620b62Ea65cD10914801ce062b436Bb5"
STREAMER_OWNER_ADDRESS = "0x0F3e0c4218b7b0108a3643cFe9D3ec0d4F57c54e" ## authorizer-adaptor



##  Accounts
@pytest.fixture(scope="session")
def admin():
    return accounts[1]


@pytest.fixture(scope="session")
def authorizer_adaptor():
    return STREAMER_OWNER_ADDRESS


@pytest.fixture(scope="session")
def streamer():
    return interface.IChildChainStreamer(STREAMER_ADDRESS)



@pytest.fixture(scope="session")
def upkeep_caller():
    return accounts[2]


@pytest.fixture(scope="session")
def deployer():
    return accounts[0]


@pytest.fixture(scope="session")
def injector(deploy):
    return deploy.injector


@pytest.fixture(scope="session")
def token(deploy):
    return deploy.token


@pytest.fixture(scope="session")
def deploy(deployer, admin, upkeep_caller, authorizer_adaptor, streamer):
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
    injector.setRecipientList([streamer.address], [100], [3], {"from": admin})

    return DotMap(
        injector=injector,
        token=token,
    )


