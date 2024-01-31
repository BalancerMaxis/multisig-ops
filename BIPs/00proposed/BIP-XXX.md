# Payload
https://github.com/BalancerMaxis/multisig-ops/pull/780

# TL;DR:

This BIP is concerning what to do with $376k USD in losses reported pertaining to the linear pool hack from last year.

It proposes back paying holders 75% of the lost value in BAL by way of a direct airdrop based on the discussion held here: https://forum.balancer.fi/t/rfc-linear-pool-hack-restitution/5504.

If passed, BAL amounts will be finally calculated based on pricing before a direct airdrop TX is loaded.  Based on current pricing the total amount is 75,026 $BAL.

If any users bring up concerns about being dropped BAL, they may request themselves to be removed before the final payload is loaded on Monday.  We can then handle that in separate governance.


# Background:

Last year, Balancer, a whitehat found a [vulnerability in Balancer’s linear pools ](https://medium.com/balancer-protocol/rate-manipulation-in-balancer-boosted-pools-technical-postmortem-53db4b642492). Mitigations were put in place for many pools, and a strong [comms effort](https://twitter.com/functi0nZer0/status/1694107340079792477) was initiated to try to reach depositors in the pools that could be mitigated, asking them to withdraw. 5 days after the vulnerability was announced, hackers figured out the exploit and remaining funds in vulnerable pools were drained.

Following the passage of [BIP-445](https://forum.balancer.fi/t/bip-445-decide-on-direction-of-restitution-for-affected-lps-in-boosted-pool-incident), a 90 day collection period was completed. Multiple reminders were sent out over various channels, the most recent of which was this [Tweet](https://twitter.com/Balancer/status/1738158848827912214). This RFC presents the results of the research on the resulting dataset of claims, and asks veBAL voters to decide on how to restitute the victims. Once final details are decided in this RFC, a BIP will be posted with similar contents to approve the decision.

# Details

# The Claims Data set:

Users were sent to a[ UI element](https://app.balancer.fi/#/ethereum/claim-submission) that requested transaction IDs withdraws from hacked pools. These requests were submitted on chain to this [Smart Contract ](https://etherscan.io/address/0x70b55Af71B29c5Ca7e67bD1995250364C4bE5554#events), which generated events for each claim. Note that the claims period is now closed, using the UI element to report a loss now will not result in it being considered.

The events were collected and imported into this [google sheet ](https://docs.google.com/spreadsheets/d/1oAAqh2fJnR4EwnHYiKzuJoWZfy1GxmOPTkDj2SAR71I/edit#gid=1476637663), where research was conducted and results were obtained. In the end 41 addresses reported losses. Of those, 4 addresses did not show any on-chain evidence of loss. A vast majority of the losses came from the bb-a-usd pool. The total USD value lost, based on pricing at time of hack adds up to $376,032.42. $5,861.27 of these losses were from 2 wallets on Optimism, the rest from mainnet.

The shape and style of Compensation:

# The form of payment:

A major narrative over the last year at Balancer has been building/maintaining a stable USD runway. Things have improved recently, but Balancer is not USD rich. For that reason, it is proposed that restitution be paid in BAL tokens. The amount of BAL tokens paid should be based on a 24 hour TWAP preceding the posting of the snapshot (on a Thursday).

# The delivery of payment:

On mainnet, payment will be directly airdropped to affected wallets in the same week that voting ends.
The addresses on Optimism do not look like they have gas on mainnet. Further, Beets has signalled its willingness to assist with distribution, and potentially cover half of the costs of repayment for Beets users on OP. For this reason, it is suggested that 50% of the BAL due to OP users is sent to Beethoven X on mainnet, and Beethoven then takes responsibility for restitution to the users for the full amount due directly on Optimsm. If beet governance decides not to pay half of the costs, the final proposal will be changed such that 100% of the BAL due to OP users is sent to beets.

# The amount of payment:

An RFC was held https://forum.balancer.fi/t/rfc-linear-pool-hack-restitution/5504 to collect community feedback around this issue.  A poll was staged asking if this BIP should offer 75% of the amount lost or 100% and opened the floor to discuss other options.  
In the discussion the primary other option that people thought should be included was 0, or no restitution, but a rejection of this BIP has the same functional effect while not blocking further governance. 

 - More inidividuals selected the 75% option to the 25% option.  
 - A number of major hodlers or delegates polled on both sides
   - @humpydumpy007 and a number of other sizeable delegates choosing  75%, 
   - @jameskbh was the only delegate with real vote weight choosing 100% .  
  
Therefore this BIP proposes that 75% of the amount lost is paid back.  This results in a total of **AMOUNT???** USD of value, which results in a total of **AMOUNT??** BAL at the time of this vote.   If the price of BAL moves by more than 5 cents by noon on Monday after a successful yes vote, the payload will be regenerated using new BAL pricing and the total amount of BAL paid out may change.

Finally, Bethooven has agreed to pay half of the  **AMOUNT?? in USD** due to victims as decided by Balancer, which is 50% of the final value owed to Optimsim based victims will be sent to the Beets Treasury on Mainnet `0x811912c19eEF91b9Dc3cA52fc426590cFB84FC86`. This reduces the total amount due to Balancer by **AMOUNT**

# Specification

Around Noon GMT on Monday the final price of BAL should be checked.  If it deviates from the current payload price of 3.65 by more then 5 cents, the payload CSV will be renegerated from the google sheet using the new current price.  The final payload will then be reviewed by at least 2 Balancer Maxis on github before being loaded into the DAO multisig as part of the regular process.

# The List of Payouts
The current CSV, that may be revised based on BAL pricing and does not include Optimsim victims, but does include the Beethoven Treasury is below.  If you reported, please check this.  If you will be unable to access $BAL sent to this address, please comment on this forum post or contact @gosuto or myself or any of the Maxis here or on [Discord](https://discord.balancer.fi).


**MD Table of address/usd lost/ BAL to airdrop/ USD value**