import pytest
import time
from brownie import (
    interface,
    accounts,
    periodicRewardsInjector,
    testToken,

)

STREAMER_ADDRESS = "0x48B024C6620b62Ea65cD10914801ce062b436Bb5"
STREAMER_OWNER_ADDRESS = "0xc38c5f97B34E175FFd35407fc91a937300E33860"

from rich.console import Console

console = Console()

from dotmap import DotMap
import pytest


##  Accounts
@pytest.fixture(scope="session")
def admin():
    return accounts[1]


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
def streamer(deploy):
    return deploy.streamer


@pytest.fixture(scope="session")
def deploy(deployer, admin, upkeep_caller):
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
    injector.setRecipientList([STREAMER_ADDRESS], [100], [3], {"from": admin})

    return DotMap(
        deployer=deployer,
        injector=injector,
        token=token,
        registry=upkeep_caller,
        streamer=interface.IChildChainStreamer(STREAMER_ADDRESS),
        admin=admin,
    )


