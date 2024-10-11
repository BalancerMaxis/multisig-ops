# veBalFeesInjector

This contract/upkeep is meant to handle the regular injection of veBAL fees.  You can find the repo [here](https://github.com/BalancerMaxis/veBalFeeInjector).  It is intended to take biweekly outputs of fee processing operations in the configured tokens, and pay them out out over a 2 one week periods.


The payout occurs by paying half of the total amount one week, and then the full amount the next, then half, then all.  As a result, 2 weeks fees injected will result in half paid one week, and the remainder paid the following week.


The contract includes admin functions to change the handled tokens and sweep ERC20s and gas tokens.

You can find out more information about the tokens handled, by calling getTokens() in the read functions of the contract.

Etherscan: https://etherscan.io/address/0x8AD2512819A7eae1dd398973EFfaE48dafBe8255#readContract
Chainlink Upkeep: https://automation.chain.link/mainnet/272064120448970968129350878338658121801758038303433171306878704282507266745

This contract and upkeep is owned by the lm multisig.

## When does it run
The injection should run as close to possible to the turn of the epoch.  This injected the fees that will be delivered and the start of the epoch that follows (next next epoch).
