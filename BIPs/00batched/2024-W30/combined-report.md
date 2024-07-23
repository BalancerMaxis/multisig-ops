
## Mainnet DAO Multisig

[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/1c84d54d-4aaa-44cb-9180-51e2e12e79f5)
[Reject Nonce 250 - will fail, Sign Nonce 251](https://app.safe.global/transactions/queue?safe=eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)

Note that Nonce 250 was loaded without using the authorizer adapter, tenderly showed success, and it was only caught in final review after loading.  250 will fail to exec.  The original [Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/a074f965-8fc8-4cb8-b480-b27f40af8015) shows an end state of success but does show the revert.  
251 is the corrected version that calls admin functions the gauge through the AuthorizerAdapter

FILENAME: `BIPs/00batched/2024-W29/1-0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f.json`
MULTISIG: `multisigs/dao (mainnet:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)`
COMMIT: `632e2e90b71fe972ba0a55a2c8595f1b631f7ab2`
CHAIN(S): `mainnet`
TENDERLY: [SUCCESS](https://www.tdly.co/shared/simulation/a97fdaf3-6e04-4c84-883a-85ee76b52c1a)
```
+-----------------------+---------------+--------------------------------------------+--------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name   | caller_address                             | fx_paths                                                                                   | action_ids                                                         |   bip   | tx_index |
+-----------------------+---------------+--------------------------------------------+--------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRole  | multisigs/dao | 0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f | 20220325-mainnet-gauge-factory/LiquidityGaugeV5/set_reward_distributor(address,address)    | 0xd0090a09f425bba74e6c801fba7c6d15b44147ab0bd319e40076ce07e95168b6 | BIP-653 |    0     |
|                       |               |                                            | 20220822-mainnet-gauge-factory-v2/LiquidityGaugeV5/set_reward_distributor(address,address) |                                                                    |         |          |
| Authorizer/revokeRole | multisigs/dao | 0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f | 20220325-mainnet-gauge-factory/LiquidityGaugeV5/set_reward_distributor(address,address)    | 0xd0090a09f425bba74e6c801fba7c6d15b44147ab0bd319e40076ce07e95168b6 | BIP-653 |    4     |
|                       |               |                                            | 20220822-mainnet-gauge-factory-v2/LiquidityGaugeV5/set_reward_distributor(address,address) |                                                                    |         |          |
+-----------------------+---------------+--------------------------------------------+--------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```
```
+------------------------+-------------------------------------------------------------------------------+-------+---------------------------------------------------------------------------+------------+----------+
| fx_name                | to                                                                            | value | inputs                                                                    | bip_number | tx_index |
+------------------------+-------------------------------------------------------------------------------+-------+---------------------------------------------------------------------------+------------+----------+
| set_reward_distributor | 0xBC02eF87f4E15EF78A571f3B2aDcC726Fee70d8b (gauges/DOLA-USDC BSP-gauge-bc02)  | 0     | {                                                                         | BIP-653    |   N/A    |
|                        |                                                                               |       |   "_reward_token": [                                                      |            |          |
|                        |                                                                               |       |     "0x41D5D79431A913C4aE7d69a668ecdfE5fF9DFB68 (tokens/INV)"             |            |          |
|                        |                                                                               |       |   ],                                                                      |            |          |
|                        |                                                                               |       |   "_distributor": [                                                       |            |          |
|                        |                                                                               |       |     "0xfEb352930cA196a80B708CDD5dcb4eCA94805daB (paladin/QuestBoardV2_1)" |            |          |
|                        |                                                                               |       |   ]                                                                       |            |          |
|                        |                                                                               |       | }                                                                         |            |          |
| set_reward_distributor | 0xCD19892916929F013930ed628547Cc1F439b230e (gauges/sDOLA-DOLA BSP-gauge-cd19) | 0     | {                                                                         | BIP-653    |   N/A    |
|                        |                                                                               |       |   "_reward_token": [                                                      |            |          |
|                        |                                                                               |       |     "0x41D5D79431A913C4aE7d69a668ecdfE5fF9DFB68 (tokens/INV)"             |            |          |
|                        |                                                                               |       |   ],                                                                      |            |          |
|                        |                                                                               |       |   "_distributor": [                                                       |            |          |
|                        |                                                                               |       |     "0xfEb352930cA196a80B708CDD5dcb4eCA94805daB (paladin/QuestBoardV2_1)" |            |          |
|                        |                                                                               |       |   ]                                                                       |            |          |
|                        |                                                                               |       | }                                                                         |            |          |
| set_reward_distributor | 0x21c377cBB2bEdDd8534308E5CdfeBE35fDF817E8 (gauges/2BTC-gauge-21c3)           | 0     | {                                                                         | BIP-653    |   N/A    |
|                        |                                                                               |       |   "_reward_token": [                                                      |            |          |
|                        |                                                                               |       |     "0xCdF7028ceAB81fA0C6971208e83fa7872994beE5 (tokens/T)"               |            |          |
|                        |                                                                               |       |   ],                                                                      |            |          |
|                        |                                                                               |       |   "_distributor": [                                                       |            |          |
|                        |                                                                               |       |     "0xfEb352930cA196a80B708CDD5dcb4eCA94805daB (paladin/QuestBoardV2_1)" |            |          |
|                        |                                                                               |       |   ]                                                                       |            |          |
|                        |                                                                               |       | }                                                                         |            |          |
+------------------------+-------------------------------------------------------------------------------+-------+---------------------------------------------------------------------------+------------+----------+
```
## Optimism DAO Multisig
[Sign Nonce 31](https://app.safe.global/transactions/queue?safe=oeth:0x043f9687842771b3dF8852c1E9801DCAeED3f6bc)

Note this was loaded in Week-29 but delayed due to no critical operatiions.


FILENAME: `BIPs/00batched/2024-W29/10-0x043f9687842771b3dF8852c1E9801DCAeED3f6bc.json`
MULTISIG: `multisigs/dao (optimism:0x043f9687842771b3dF8852c1E9801DCAeED3f6bc)`
COMMIT: `632e2e90b71fe972ba0a55a2c8595f1b631f7ab2`
CHAIN(S): `optimism`
TENDERLY: [SUCCESS](https://www.tdly.co/shared/simulation/259bad4d-ddf1-4ea5-b252-cdf6091526c9)
```
+----------------------+--------------------+--------------------------------------------+------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function             | caller_name        | caller_address                             | fx_paths                                                                                                   | action_ids                                                         |   bip   | tx_index |
+----------------------+--------------------+--------------------------------------------+------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRole | mimic/smartVaultV3 | 0x9e5D6427D2cdaDC68870197b099C2Df535Ec3c97 | 20220517-protocol-fee-withdrawer/ProtocolFeesWithdrawer/withdrawCollectedFees(address[],uint256[],address) | 0x5a57bdde85c7a823e064d8cdc9a9a1b617f739068ec8925eaf6a562aa22513c6 | BIP-651 |    0     |
+----------------------+--------------------+--------------------------------------------+------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```


## Fraxtal DAO multisig
[Sign Nonce 4](https://safe.optimism.io/transactions/queue?safe=fraxtal:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e)

FILENAME: `BIPs/00batched/2024-W29/252-0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e.json`
MULTISIG: `multisigs/lm (fraxtal:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e)`
COMMIT: `632e2e90b71fe972ba0a55a2c8595f1b631f7ab2`
CHAIN(S): `fraxtal`
TENDERLY: [SUCCESS](https://www.tdly.co/shared/simulation/c3e814c3-68e5-4fbf-bae6-7517a6666362)
```
+-------------------------+---------------------------------------------------------------------------------------------------------+-------+---------------------------------------------------------------------------------------------------------------+------------+----------+
| fx_name                 | to                                                                                                      | value | inputs                                                                                                        | bip_number | tx_index |
+-------------------------+---------------------------------------------------------------------------------------------------------+-------+---------------------------------------------------------------------------------------------------------------+------------+----------+
| setTrustedRemoteAddress | 0xE241C6e48CA045C7f631600a0f1403b2bFea05ad (20230524-lz-omni-voting-escrow-child/OmniVotingEscrowChild) | 0     | {                                                                                                             | BIP-660    |   N/A    |
|                         |                                                                                                         |       |   "_remoteChainId": [                                                                                         |            |          |
|                         |                                                                                                         |       |     "101"                                                                                                     |            |          |
|                         |                                                                                                         |       |   ],                                                                                                          |            |          |
|                         |                                                                                                         |       |   "_remoteAddress": [                                                                                         |            |          |
|                         |                                                                                                         |       |     "0xE241C6e48CA045C7f631600a0f1403b2bFea05ad (20230524-lz-omni-voting-escrow-child/OmniVotingEscrowChild)" |            |          |
|                         |                                                                                                         |       |   ]                                                                                                           |            |          |
|                         |                                                                                                         |       | }                                                                                                             |            |          |
+-------------------------+---------------------------------------------------------------------------------------------------------+-------+---------------------------------------------------------------------------------------------------------------+------------+----------+
```
## MODE DAO Multisig
Please reject Nonce 4.  The fraxtal payload above was loaded on the wrong safe due to some confusion with new chain_ids, the non-standard safe interface, and the lack of tenderly to check things. 