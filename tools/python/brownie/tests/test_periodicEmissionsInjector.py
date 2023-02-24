import brownie
import time
from brownie import chain
import pytest

STREAMER_STUCK = 6003155 ## Something that seems stuck in the streamer LDO
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

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
    injector.setRecipientList([streamer.address], [100], [2], {"from": admin})
    upkeepNeeded, performData = injector.checkUpkeep.call(
        "",
        {"from": upkeep_caller},
    )
    assert isinstance(upkeepNeeded, bool)
    assert isinstance(performData, bytes)


def test_can_perform_first_upkeep_(injector, upkeep_caller, streamer, token, admin, whale, gauge,weekly_incentive):
    ## Setup [2] for 2 rounds
    assert(weekly_incentive * 3 > token.balanceOf(admin)) # Tokens for 3 rounds so we are stopped by max rounds in the injector config
    injector.setRecipientList([streamer.address], [weekly_incentive], [2], {"from": admin})
    reward_data = streamer.reward_data(token)
    ## Advance to the next Epoch
    (upkeepNeeded, performData) = injector.checkUpkeep("", {"from": upkeep_caller})
    if upkeepNeeded is False:
        sleep_time = (reward_data[1] - chain.time())  # about 1 block after the peroiod ends.
        chain.sleep(sleep_time)
        chain.mine()
        (upkeepNeeded, performData) = injector.checkUpkeep(
            "",
            {"from": upkeep_caller},
        )
        assert(upkeepNeeded is True)
    ## Test perform upkeep for the first round
    initial_system_balance  = token.balanceOf(streamer) + token.balanceOf(gauge)
    assert(token.balanceOf(injector) >= weekly_incentive)  # injector should have coinz
    assert(injector.performUpkeep(performData, {"from": upkeep_caller})) # Perform upkeep
    assert(token.balanceOf(streamer) - STREAMER_STUCK == weekly_incentive)  # Tokens are in place
    assert(initial_system_balance - STREAMER_STUCK == token.balanceOf(gauge) )
    ## advance time and check that claim reduces streamer balancer
    initial_steramer_balance = token.balanceOf(streamer)
    (upkeepNeeded, performData) = injector.checkUpkeep("", {"from": upkeep_caller})
    assert(upkeepNeeded==False)  ## not time yet
    r1_streamer_balance = token.balanceOf(streamer)
    chain.mine()
    chain.sleep(300)
    chain.mine()
    (upkeepNeeded, performData) = injector.checkUpkeep("",{"from": ZERO_ADDRESS})
    assert(upkeepNeeded == False) # not time yet
    claim = gauge.claim_rewards({"from": whale})
    assert(token.balanceOf(streamer) < r1_streamer_balance)  # Whale pulled tokens from streamer on claim

    # sleep till second epoch
    chain.sleep(60*60*24*8) # 8 days should be more than a 1 week epoch
    chain.mine()
    (upkeepNeeded, performData) = injector.checkUpkeep("",{"from": ZERO_ADDRESS})
    assert(upkeepNeeded == True)
    # Test second upkeep
    initial_system_balance  = token.balanceOf(streamer) + token.balanceOf(gauge)
    assert(injector.performUpkeep(performData, {"from": upkeep_caller})) # Perform upkeep
    assert ( (token.balanceOf(streamer) + token.balanceOf(gauge)) - initial_system_balance == weekly_incentive)  # injector should have new coinz
    (upkeepNeeded, performData) = injector.checkUpkeep("", {"from": ZERO_ADDRESS})
    assert (upkeepNeeded == False)  # not time yet

    #check third epcoh we stop
    chain.sleep(60 * 60 * 24 * 8)  # 8 days should be more than a 1 week epoch
    chain.mine()
    (upkeepNeeded, performData) = injector.checkUpkeep("", {"from": ZERO_ADDRESS})
    assert (upkeepNeeded == False)  # No more runs



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


