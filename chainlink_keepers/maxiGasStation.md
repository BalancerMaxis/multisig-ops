## The Maxi Gas Station - Chainlink Automation

#### Note that this facility is currently only operational on mainnet and everything here refers to that

The Maxi Gas Station (v2) is currently active and running on the following chains at the following addresses:

| Chain   | Etherscan                                                                |
|---------|--------------------------------------------------------------------------|
| Mainnet | https://etherscan.io/address/0x7fb8f5D04b521B6880158819E69538655AABD5c4  |


The holds ETH(or whatever a chains native gas token is), and manages the configuration about when gas needs to be paid out.

The Chainlink automation page describing chain links interaction with this contract to automate can be found [HERE](https://automation.chain.link/mainnet/62602467182204477380138952081172885895406053754821061796893606503759482417757).  You can also top up link needed to cover the costs of triggering the contract.


The chainlink side of the automation can be found here: 
The list of watched addresses that may be refilled can be found by calling  `GetWatchList` on the [Maxi GasStation contract](https://etherscan.io/address/0x2F1901f2A82fcC3Ee9010b809938816B3b06FA6A#readContract).

The specific parameters for a given watchlist address can be found by calling `getAccountsInfo(address)` for an address on the watchlist.  The outputs look like this:
```
[ getAccountInfo(address) method Response ]
  isActive   bool :  true
  minBalanceWei   uint96 :  500000000000000000
  topUpToAmountWei   uint96 :  1000000000000000000
  lastTopUpTimestamp   uint56 :  1676923715
```
**minBalanceWei:** defines the target minimum ETH balance for this address.
**topUpToAmountWei:** defines the minimum amount of ETH that will be sent as part of a topup.

In the configuration above 0.5 ETH minBalance and 1 ETH TopUpToAmount means that the given wall should always have between 0.5 and 1 ETH.  The gas station will top the wallet up to 1 ETH any time it falls below 0.5.

You can add new recipients or change the configuration of current ones by calling (addRecipients()).  You can remove addresses from the watch list entirely by calling removeRecipients()

### It's not working, what could be wrong.
Check the [Automation Page](https://automation.chain.link/mainnet/49137003109931569296061861008543141201993692712511923124729013217194676883059) and make sure there is enough LINK.  If not you can use the button to fund the upkeep with more.
![img.png](../docs/images/fundUpkeep.png)

Check the [GasStation contract](https://etherscan.io/address/0x7fb8f5D04b521B6880158819E69538655AABD5c4#writeContract): 

- Does it have enough ETH?  Just send ETH to the contract to fund with more.
   -  The gas station should fire if there is any watched wallet that has below minAmount and can be topped up to topUpToAmount, even if all the needy wallets together make up more than the eth in the station. 
- does the read function `checkUpkeep("0x")` return TRUE with some calldata, if so then LINK should be linking.
- Has it been under minWaitPeriod(read function) since the address needing was last topped up?

If you still haven't figured out what is wrong, talk to Tritium and/or take a minute to think about the watchlists and the current state of things.

Check Upkeep will not return True unless the following reasonably selfExplanitory if statement returns true:

```solidity
if (recipient.balance < target.minBalanceWei) {// Wallet needs funding
    uint256 delta = target.topUpToAmountWei - recipient.balance;
    if (
        target.lastTopUpTimestamp + minWaitPeriod <= block.timestamp && // Not too fast
        balance >= delta // we have the bags
    ) 
    {}
}
```

### How can I learn more about chainlink automation
[DOCS](https://docs.chain.link/chainlink-automation/introduction)