import brownie
import time
from brownie import chain
import pytest

STREAMER_STUCK = 6003155 ## Something that seems stuck in the streamer LDO

def test_deploy(deploy):
    return

def test_set_recipient_list(injector, admin, streamer):
    recipients = [streamer]
    amounts = [100]
    periods = [3]
    injector.setRecipientList(recipients, amounts, periods, {"from": admin})
    assert injector.getWatchList() == recipients
    assert injector.getAccountInfo(recipients[0]) == (True, 100, 3, 0, 0)


def test_can_call_check_upkeep(upkeep_caller, injector, streamer, admin):
    # Arrange
    injector.setRecipientList([streamer.address], [100], [3], {"from": admin})
    upkeepNeeded, performData = injector.checkUpkeep.call(
        "",
        {"from": upkeep_caller},
    )
    assert isinstance(upkeepNeeded, bool)
    assert isinstance(performData, bytes)


def test_can_perform_first_upkeep_(injector, upkeep_caller, streamer, token, admin, whale, gauge,weekly_incentive):
    assert(weekly_incentive * 3 > token.balanceOf(admin)) # we have enough coinz
    injector.setRecipientList([streamer.address], [weekly_incentive], [3], {"from": admin})
    reward_data = streamer.reward_data(token)
    print(injector.checkUpkeep("", {"from": upkeep_caller}))
    (upkeepNeeded, performData) = injector.checkUpkeep(
        "",
        {"from": upkeep_caller},
    )

    ## advance time and check that claim reduces streamer balancer
    initial_steramer_balance = token.balanceOf(streamer)
    reward_data = streamer.reward_data(token)
    assert(reward_data[1] > chain.time())  # New period finish
    chain.mine()
    chain.sleep(300)
    chain.mine()
    claim = gauge.claim_rewards({"from": whale})
    assert(token.balanceOf(streamer) < initial_steramer_balance)  # Whale pulled tokens from streamer on claim

    chain.sleep(60*60*24*8) # 8 days should be more than a 1 week epoch

    (upkeepNeeded, performData) = injector.checkUpkeep("",{"from": ZERO_ADDRESS})
    assert upkeepNeeded == true:


def test_non_authorized_caller:


def test_
def test_pause_and_unpause(injector, admin, upkeep_caller):
    # Pause the contract
    injector.pause({"from": admin})
    assert injector.paused({"from": admin}) is True

    # Wait for the minimum wait period and trigger injection (should fail due to pause)
    chain.sleep(injector.getMinWaitPeriodSeconds())
    with brownie.reverts("Pausable: paused"):
        injector.checkUpkeep("")

    # Unpause the contract
    injector.unpause({"from": admin})
    assert injector.paused({"from": admin}) is False


