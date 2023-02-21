import brownie
import time
from brownie import chain
import pytest

def test_deploy(deploy):
    return

def test_set_recipient_list(injector, admin, streamer):
    recipients = [streamer]
    amounts = [100]
    periods = [3]
    injector.setRecipientList(recipients, amounts, periods, {"from": admin})
    assert injector.getWatchList() == recipients
    assert injector.getAccountInfo(recipients[0]) == (True, 100, 3, 0, 0)


def test_can_call_check_upkeep(upkeep_caller, injector):
    # Arrange
    upkeepNeeded, performData = injector.checkUpkeep.call(
        "",
        {"from": upkeep_caller},
    )
    assert isinstance(upkeepNeeded, bool)
    assert isinstance(performData, bytes)

def test_can_perform_upkeep(injector, upkeep_caller, streamer, token):
    reward_data = streamer.reward_data(token)
    if reward_data[1] <= chain.time():
        print (reward_data[1])
        chain.sleep(chain.time() - reward_data[1]+1)
        reward_data = streamer.reward_data(token)  # grab new rewad data fter the fast forward
    print(injector.checkUpkeep("", {"from": upkeep_caller}))
    (upkeepNeeded, performData) = injector.checkUpkeep(
        "",
        {"from": upkeep_caller},
    )
    assert(upkeepNeeded is True)
    assert(token.balanceOf(streamer) is 0)  # streamer should be empty
    assert(token.balanceOf(injector) >= 100)  # injector should have coinz
    assert(streamer.performUpkeep(performData), {"from": upkeep_caller}) # Perform upkeep
    assert(token.balanceOf(streamer) == 100) # Tokens are in place
    assert(reward_data[1] > chain.time())  # New period finish
    chain.mine()
    chain.sleep(300)
    chain.mine()
    assert(token.balanceOf(streamer) < 100) # Tokens are in place



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


