# Payload

https://github.com/BalancerMaxis/multisig-ops/pull/780

# TL;DR:

This BIP is concerning what to do with $376k USD in losses reported pertaining to the linear pool hack from last year.

It proposes back paying holders 75% of the lost value in BAL by way of a direct airdrop based on the discussion held here: https://forum.balancer.fi/t/rfc-linear-pool-hack-restitution/5504.

If passed, BAL amounts will be finally calculated based on pricing before a direct airdrop TX is loaded. Based on current pricing the total amount is 75,475 $BAL.

If any users bring up concerns about being dropped BAL, they may request themselves to be removed before the final payload is loaded on Monday. We can then handle that in separate governance.

# Background:

Last year, Balancer, a whitehat found a [vulnerability in Balancer’s linear pools ](https://medium.com/balancer-protocol/rate-manipulation-in-balancer-boosted-pools-technical-postmortem-53db4b642492). Mitigations were put in place for many pools, and a strong [comms effort](https://twitter.com/functi0nZer0/status/1694107340079792477) was initiated to try to reach depositors in the pools that could be mitigated, asking them to withdraw. 5 days after the vulnerability was announced, hackers figured out the exploit and remaining funds in vulnerable pools were drained.

Following the passage of [BIP-445](https://forum.balancer.fi/t/bip-445-decide-on-direction-of-restitution-for-affected-lps-in-boosted-pool-incident), a 90 day collection period was completed. Multiple reminders were sent out over various channels, the most recent of which was this [Tweet](https://twitter.com/Balancer/status/1738158848827912214). This RFC presents the results of the research on the resulting dataset of claims, and asks veBAL voters to decide on how to restitute the victims. Once final details are decided in this RFC, a BIP will be posted with similar contents to approve the decision.

# Details

## The Claims Data set:

Users were sent to an [UI element](https://app.balancer.fi/#/ethereum/claim-submission) that requested transaction IDs withdraws from hacked pools. These requests were submitted on chain to this [Smart Contract ](https://etherscan.io/address/0x70b55Af71B29c5Ca7e67bD1995250364C4bE5554#events), which generated events for each claim. Note that the claims period is now closed, using the UI element to report a loss now will not result in it being considered.

The events were collected and imported into this [google sheet ](https://docs.google.com/spreadsheets/d/1oAAqh2fJnR4EwnHYiKzuJoWZfy1GxmOPTkDj2SAR71I/edit#gid=1476637663), where research was conducted and results were obtained. In the end 41 addresses reported losses. Of those, 4 addresses did not show any on-chain evidence of loss. A vast majority of the losses came from the bb-a-usd pool. The total USD value lost, based on pricing at time of hack adds up to $376,032.42. $5,861.27 of these losses were from 2 wallets on Optimism, the rest from mainnet.

The shape and style of Compensation:

## The form of payment:

A major narrative over the last year at Balancer has been building/maintaining a stable USD runway. Things have improved recently, but Balancer is not USD rich. For that reason, it is proposed that restitution be paid in BAL tokens. The amount of BAL tokens paid should be based on a 24 hour TWAP preceding the posting of the snapshot (on a Thursday).

## The delivery of payment:

On mainnet, payment will be directly airdropped to affected wallets in the same week that voting ends.
The addresses on Optimism do not look like they have gas on mainnet. Further, Beets has signalled its willingness to assist with distribution, and potentially cover half of the costs of repayment for Beets users on OP. For this reason, it is suggested that 50% of the BAL due to OP users is sent to Beethoven X on mainnet, and Beethoven then takes responsibility for restitution to the users for the full amount due directly on Optimsm. If beet governance decides not to pay half of the costs, the final proposal will be changed such that 100% of the BAL due to OP users is sent to beets.

## The amount of payment:

An [RFC was held](https://forum.balancer.fi/t/rfc-linear-pool-hack-restitution/5504) to collect community feedback around this issue. A poll was staged asking if this BIP should offer 75% of the amount lost or 100% and opened the floor to discuss other options.

As a [result of said conversation](https://forum.balancer.fi/t/rfc-linear-pool-hack-restitution/5504/15?u=tritium), this BIP proposes that 75% of the amount lost is paid back. This results in a total of `376_032.42 * .75 = 282_024.32` USD of value, which results in a total of `282_024.32 / 3.57 = 78_998.40896359` BAL at the time of this vote. If the price of BAL moves by more than 5 cents by noon on Monday after a successful yes vote, the payload will be regenerated using new BAL pricing and the total amount of BAL paid out may change.

# Extra decisions and details surrounding this matter

## Beethoven helps out with losses on Optimism
Beethoven has agreed to pay half of the `5_861.28 * .75 = 4_395.96` USD due to victims as decided by Balancer, which is 50% of the final value owed to Optimsim based victims will be sent to the Beets Treasury on Mainnet `0x811912c19eEF91b9Dc3cA52fc426590cFB84FC86`. This reduces the total amount due by Balancer by `615.68067227` BAL (see first row of the airdrop csv).

## Addition of a late reporter on Arbitrum with special handling
A user with the address [0x8484e288b7c2edad1b5214ed9df3bae4af7dadf5](https://arbiscan.io/address/0x8484e288b7c2edad1b5214ed9df3bae4af7dadf5) showed up on Discord after the end of the claim period reporting [losses](https://arbiscan.io/tx/0xe135f72acc1214b05fb68a1977d11a951960bb3fa323b2ab2b3fdf8f4d159c96) from the USD+ pool on Arbitrum. The total losses were calculated using the same methods as other claimants:
`pre-hack value = 2_312.80701209198413362 BPTs * 1.01542668 USDperBPT = 2_348.48594577 USD`
`recovered value wUSD+ = 106.19`
`recpvered value USD = (106.19 USD in USD+) + (66.35 USDC) = 172.54 `
`total loss = 2_312.8070120919841336 -  172.54 = 2140.267012092 in USD vaue lost`
Support and the Balancer Maxis agreed to include this address in this restituion BIP barring any strong objections stated in comments before snapshot.

Based on the 75% payback at the currently used BAL price this equates to `2140.267012092 * .75 / 3.57 = 449.6359269101 $BAL`.  As with other claims this amount will be recalculated if the price of BAL drops more than 5 cents.

Further this user is the sole Arbitrum claimant, and does not have gas on mainnet.  The Balancer Maxis still have 1,287 $BAL in the [Op LM Multisig](https://app.safe.global/balances?safe=oeth:0x09Df1626110803C7b3b07085Ef1E053494155089).  This BAL was left over from the [entry into BAL/ETH LP](https://forum.balancer.fi/t/bip-524-seed-bal-liquidity-on-optimism/5474) due to price movements between snapshot and deposit.  The plan was to bridge these assets back to the DAO multisig on mainnet, but this BIP proposes that this BAL is instead held on Op to be used there as instructed by governance, with a portion of it being used to pay back the affected user described above.  The user has agreed to accept payment on Optimsim for their Arbitrum based losses. 



# Specification

Around Noon GMT on Monday the final price of BAL should be checked. If it deviates from the current payload price of `$3.57` by more then 5 cents, the payload CSV will be renegerated from the google sheet using the new current price. The final payload will then be reviewed by at least 2 Balancer Maxis on github before being loaded into the DAO multisig as part of the regular process.

The Maxis are authorized to hold upto 1300 BAL in the Op LM multisig, and use a portion of that to pay back `1605.200259069` USD worth of BAL to `0x8484e288b7c2edad1b5214ed9df3bae4af7dadf5` on Optimism.  Remaining BAL in this safe will stay put until future governance specifies otherwise.


# The List of Payouts

The current CSV, that may be revised based on BAL pricing and does not include Optimsim victims, but does include the Beethoven Treasury is below. If you reported, please check this. If you will be unable to access $BAL sent to this address, please comment on this forum post or contact @gosuto or myself or any of the Maxis here or on [Discord](https://discord.balancer.fi).

| receiver                                   | amount (BAL)           |
| ------------------------------------------ |------------------------|
| 0x811912c19eEF91b9Dc3cA52fc426590cFB84FC86 | 615.680672270000000000 |
| 0x0412ed8438b5fae246606909ef8ba365f9103783 | 9990.995101387800      |
| 0x4281e53938c3b1c1d3e8afd21c02ce8512cdbc93 | 8942.947050640030      |
| 0xbb19053e031d9b2b364351b21a8ed3568b21399b | 5482.156847619760      |
| 0x6aee9dc09702dffab334f3f8e6f3f97c0e7261f4 | 3977.461595932680      |
| 0xda6b2a5e0c56542984d84a710f90eefd94ca1991 | 3864.324848292750      |
| 0x1c39babd4e0d7bff33bc27c6cc5a4f1d74c9f562 | 3602.251184687360      |
| 0x66c9e1e4fe518cebfe59c9de16e1c780ef5bacd3 | 3311.989335451880      |
| 0xe7a76d8513e55578c80e4b26fc61ee7d4906d4cd | 2900.083047791250      |
| 0x91b9e59614995e13a32e36440ac524825f7ae39e | 2853.241920880260      |
| 0x19ae63358648795aaf29e36733f04fcef683aa69 | 2403.861226346110      |
| 0xd519d5704b41511951c8cf9f65fee9ab9bef2611 | 2366.325069629450      |
| 0x9b71dbccd9ffb858899ef3244b09a5354b16048e | 2360.939491636720      |
| 0x74c3646adad7e196102d1fe35267adfd401a568b | 2323.821488996030      |
| 0xba5c2f2165ddd691f99e12a23ec75cc1519930b4 | 2320.708830947810      |
| 0x1cbad69d9cc22962a0a885921518c06ed2f04ffd | 2112.388067695380      |
| 0x1c8bcb6348c84122e67a50e513a1e183c0e6929a | 1884.150318266970      |
| 0x6724f3fbb16f542401bfc42c464ce91b6c31001e | 1728.214666145720      |
| 0xff052381092420b7f24cc97fded9c0c17b2cbbb9 | 1589.773016013600      |
| 0x242d7cd78cce454946f35f0a263b54fbe228852c | 1528.094110852380      |
| 0x6d5dda04760f0515dc131ff4df76a5188ffcdfcb | 1135.468489356770      |
| 0x6e33b41e44ca2be27e8f65b5231ae61a21044b4a | 1112.924127446140      |
| 0xf96cd1cf416b50b60358a17bc8593060148de422 | 1061.983717838710      |
| 0x0a29500ccc6af0b11c72d4e171d925eb0bb7ee15 | 1061.701293477720      |
| 0xd3238d8be92fd856146f53a8b6582bc88e887559 | 1060.813502101100      |
| 0xfe73b5a595405bac396c329c674571a7a3db528c | 1042.239302185270      |
| 0x438fd34eab0e80814a231a983d8bfaf507ae16d4 | 968.698971879056       |
| 0xc9cea7a3984cefd7a8d2a0405999cb62e8d206dc | 860.314807351138       |
| 0x0b177b7f10faeadd6eee6d2cc46d783f460566c8 | 820.182974078841       |
| 0xaa857ddce7b5b9cb17296c790cb40e8c11a3d4f0 | 797.803289831699       |
| 0xe68d7a6c421e2d220b5840116008c9abdbcf53b2 | 636.180089970680       |
| 0xd09ca75315e70bd3988a47958a0c6c5b30b830e1 | 614.709047199336       |
| 0x54c3c925b9d715af541b77f9817544bdc663345e | 363.682947565343       |
| 0x36cc7b13029b5dee4034745fb4f24034f3f2ffc6 | 345.292784038761       |
| 0xcaab2680d81df6b3e2ece585bb45cee97bf30cd7 | 302.655365607094       |
| 0xcb926f497763ea5cf993912a442431e6a91d5a64 | 38.666901111201        |
