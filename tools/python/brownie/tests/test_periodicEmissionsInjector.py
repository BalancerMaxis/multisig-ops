import brownie
import time

chainlink_registry = 

def test_initial_state(periodic_rewards_injector):
    assert periodic_rewards_injector.minWaitPeriodSeconds() == 60*5  # 5 mins
    assert periodic_rewards_injector.injectTokenAddress() == "0x6B175474E89094C44Da98b954EedeAC495271d0F"  # DAI
    assert periodic_rewards_injector.feeDistributorAddress() == "0x53c1dE9dC1Fb66A71C90eB6fF7317d4a6EE3b7f8"

def test_set_recipient_list(periodic_rewards_injector):
    recipients = ["0x1111111111111111111111111111111111111111", "0x2222222222222222222222222222222222222222"]
    amounts = [100, 200]
    periods = [5, 10]
    periodic_rewards_injector.setrecipientList(recipients, amounts, periods)
    assert periodic_rewards_injector.s_streamerList() == recipients
    assert periodic_rewards_injector.s_targets(recipients[0]) == (True, 100, 5, 0, 0)
    assert periodic_rewards_injector.s_targets(recipients[1]) == (True, 200, 10, 0, 0)

def test_check_upkeep(chain, my_contract):
    # Simulate a call from Chainlink
    check_data = "0x0"
    tx = my_contract.checkUpkeep(check_data, {'from': chainlink_registry})

    # Check that the upkeep was not performed immediately
    assert not tx.events

    # Fast-forward time by less than the minimum interval
    chain.sleep(my_contract.minUpkeepInterval() - 1)

    # Check that the upkeep was still not performed
    tx = my_contract.checkUpkeep(check_data, {'from': chainlink_registry})
    assert not tx.events

    # Fast-forward time by more than the minimum interval
    chain.sleep(2)

    # Check that the upkeep is performed on the next call
    tx = my_contract.checkUpkeep(check_data, {'from': chainlink_registry})
    assert tx.events['UpkeepPerformed']['checkData'] == check_data

    # Check that the upkeep cannot be performed again until enough time has passed
    tx = my_contract.checkUpkeep(check_data, {'from': chainlink_registry})
    assert not tx.events

def test_pause_and_unpause(periodic_rewards_injector):
    # Pause the contract
    periodic_rewards_injector.pause()
    assert periodic_rewards_injector.paused() == True

    # Wait for the minimum wait period and trigger injection (should fail due to pause)
    time.sleep(periodic_rewards_injector.minWaitPeriodSeconds())
    with brownie.reverts("Pausable: paused"):
        periodic_rewards_injector.trigger()

    # Unpause the contract
    periodic_rewards_injector.unpause()
    assert periodic_rewards_injector.paused() == False

    # Trigger injection (should succeed)
    periodic_rewards_injector.trigger()
