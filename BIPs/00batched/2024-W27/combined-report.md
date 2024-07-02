
## Mainnet DAO Multisig
[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/a074f965-8fc8-4cb8-b480-b27f40af8015)

[Sign Nonce 249](https://app.safe.global/transactions/queue?safe=eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)

FILENAME: `BIPs/00batched/2024-W27/1-0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f.json`
MULTISIG: `multisigs/dao (mainnet:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)`
COMMIT: `99fce6b0456b75da0c5defb882bd9570958767fc`
CHAIN(S): `mainnet`
TENDERLY: [SUCCESS](https://www.tdly.co/shared/simulation/75d4aada-bcf4-4e45-a852-333a5f595d0d)
```
+----------+------------------------------------------------+----------------------------------------------------------------------+--------------------------------------+---------+----------+
| function | token_symbol                                   | recipient                                                            | amount                               |   bip   | tx_index |
+----------+------------------------------------------------+----------------------------------------------------------------------+--------------------------------------+---------+----------+
| transfer | BAL:0xba100000625a3754423978a60c9317c58a424e3D | payees/karpatkey_payments:0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C | 5205.0 (RAW: 5205000000000000000000) | BIP-648 |    0     |
+----------+------------------------------------------------+----------------------------------------------------------------------+--------------------------------------+---------+----------+
```
FILENAME: `BIPs/00batched/2024-W27/1-0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f.json`
MULTISIG: `multisigs/dao (mainnet:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)`
COMMIT: `99fce6b0456b75da0c5defb882bd9570958767fc`
CHAIN(S): `mainnet`
TENDERLY: [SUCCESS](https://www.tdly.co/shared/simulation/81dab0da-5217-4300-920d-560f1bf46e62)
```
+------------------------+---------------+--------------------------------------------+--------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function               | caller_name   | caller_address                             | fx_paths                                                           | action_ids                                                         |   bip   | tx_index |
+------------------------+---------------+--------------------------------------------+--------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles  | multisigs/dao | 0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f | 20230519-gauge-adder-v4/GaugeAdder/setGaugeFactory(address,string) | 0x3f44776af02a9227991da37715b44e45db40735e216b3ab33144859bb6737166 | BIP-637 |    1     |
|                        |               |                                            | 20230519-gauge-adder-v4/GaugeAdder/addGaugeType(string)            | 0x2960d085c4c968d7cad55c0da3f97014525b948fdce990ecaef4e832b5f0b151 |         |          |
| Authorizer/revokeRoles | multisigs/dao | 0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f | 20230519-gauge-adder-v4/GaugeAdder/setGaugeFactory(address,string) | 0x3f44776af02a9227991da37715b44e45db40735e216b3ab33144859bb6737166 | BIP-637 |    4     |
|                        |               |                                            | 20230519-gauge-adder-v4/GaugeAdder/addGaugeType(string)            | 0x2960d085c4c968d7cad55c0da3f97014525b948fdce990ecaef4e832b5f0b151 |         |          |
+------------------------+---------------+--------------------------------------------+--------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```
FILENAME: `BIPs/00batched/2024-W27/1-0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f.json`
MULTISIG: `multisigs/dao (mainnet:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)`
COMMIT: `99fce6b0456b75da0c5defb882bd9570958767fc`
CHAIN(S): `mainnet`
TENDERLY: [SUCCESS](https://www.tdly.co/shared/simulation/59f5fe74-dba4-40a1-82dc-91978ad12e2a)
```
+---------------------+---------------------------------------------------------------------------------+-------+-------------------------------------------------------------------------------------------------------------------+------------+----------+
| fx_name             | to                                                                              | value | inputs                                                                                                            | bip_number | tx_index |
+---------------------+---------------------------------------------------------------------------------+-------+-------------------------------------------------------------------------------------------------------------------+------------+----------+
| addGaugeType        | 0x5DbAd78818D4c8958EfF2d5b95b28385A22113Cd (20230519-gauge-adder-v4/GaugeAdder) | 0     | {                                                                                                                 | BIP-637    |   N/A    |
|                     |                                                                                 |       |   "gaugeType": [                                                                                                  |            |          |
|                     |                                                                                 |       |     "Fraxtal"                                                                                                     |            |          |
|                     |                                                                                 |       |   ]                                                                                                               |            |          |
|                     |                                                                                 |       | }                                                                                                                 |            |          |
| setGaugeFactory     | 0x5DbAd78818D4c8958EfF2d5b95b28385A22113Cd (20230519-gauge-adder-v4/GaugeAdder) | 0     | {                                                                                                                 | BIP-637    |   N/A    |
|                     |                                                                                 |       |   "factory": [                                                                                                    |            |          |
|                     |                                                                                 |       |     "0x18CC3C68A5e64b40c846Aa6E45312cbcBb94f71b (20240522-fraxtal-root-gauge-factory/OptimisticRootGaugeFactory)" |            |          |
|                     |                                                                                 |       |   ],                                                                                                              |            |          |
|                     |                                                                                 |       |   "gaugeType": [                                                                                                  |            |          |
|                     |                                                                                 |       |     "Fraxtal"                                                                                                     |            |          |
|                     |                                                                                 |       |   ]                                                                                                               |            |          |
|                     |                                                                                 |       | }                                                                                                                 |            |          |
| processExpiredLocks | 0x3Fa73f1E5d8A792C80F426fc8F84FBF7Ce9bBCAC (aura/vlAURA)                        | 0     | {                                                                                                                 | BIP-638    |   N/A    |
|                     |                                                                                 |       |   "_relock": [                                                                                                    |            |          |
|                     |                                                                                 |       |     false                                                                                                         |            |          |
|                     |                                                                                 |       |   ]                                                                                                               |            |          |
|                     |                                                                                 |       | }                                                                                                                 |            |          |
| claim               | 0xFd72170339AC6d7bdda09D1eACA346B21a30D422 (aura/aura_vested_escrow)            | 0     | {                                                                                                                 | BIP-638    |   N/A    |
|                     |                                                                                 |       |   "_lock": [                                                                                                      |            |          |
|                     |                                                                                 |       |     false                                                                                                         |            |          |
|                     |                                                                                 |       |   ]                                                                                                               |            |          |
|                     |                                                                                 |       | }                                                                                                                 |            |          |
+---------------------+---------------------------------------------------------------------------------+-------+-------------------------------------------------------------------------------------------------------------------+------------+----------+
```

## Fraxtal DAO multisig
FILENAME: `BIPs/00batched/2024-W27/252-0x4f22C2784Cbd2B24a172566491Ee73fee1A63c2e.json`
MULTISIG: `multisigs/dao (fraxtal:0x4f22C2784Cbd2B24a172566491Ee73fee1A63c2e)`
COMMIT: `99fce6b0456b75da0c5defb882bd9570958767fc`
CHAIN(S): `fraxtal`
TENDERLY: [SUCCESS](https://www.tdly.co/shared/simulation/9fc340e2-6f38-43b9-9ceb-0679db089f64)
```
+------------------------+---------------+--------------------------------------------+------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function               | caller_name   | caller_address                             | fx_paths                                                                           | action_ids                                                         |   bip   | tx_index |
+------------------------+---------------+--------------------------------------------+------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles  | multisigs/dao | 0x4f22C2784Cbd2B24a172566491Ee73fee1A63c2e | 20230316-l2-ve-delegation-proxy/VotingEscrowDelegationProxy/setDelegation(address) | 0xd6a470b7515ff20313e51cfcb0941cc9bc6de272c8ef76595ca93c330a626a2f | BIP-637 |    0     |
| Authorizer/revokeRoles | multisigs/dao | 0x4f22C2784Cbd2B24a172566491Ee73fee1A63c2e | 20230316-l2-ve-delegation-proxy/VotingEscrowDelegationProxy/setDelegation(address) | 0xd6a470b7515ff20313e51cfcb0941cc9bc6de272c8ef76595ca93c330a626a2f | BIP-637 |    2     |
+------------------------+---------------+--------------------------------------------+------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```
FILENAME: `BIPs/00batched/2024-W27/252-0x4f22C2784Cbd2B24a172566491Ee73fee1A63c2e.json`
MULTISIG: `multisigs/dao (fraxtal:0x4f22C2784Cbd2B24a172566491Ee73fee1A63c2e)`
COMMIT: `99fce6b0456b75da0c5defb882bd9570958767fc`
CHAIN(S): `fraxtal`
TENDERLY: [SUCCESS](https://www.tdly.co/shared/simulation/9fd9fc25-12aa-4fc1-bec2-7b755585062a)
```
+---------------+----------------------------------------------------------------------------------------------------------+-------+-------------------------------------------------------------------------------------+------------+----------+
| fx_name       | to                                                                                                       | value | inputs                                                                              | bip_number | tx_index |
+---------------+----------------------------------------------------------------------------------------------------------+-------+-------------------------------------------------------------------------------------+------------+----------+
| setDelegation | 0xE3881627B8DeeBCCF9c23B291430a549Fc0bE5F7 (20230316-l2-ve-delegation-proxy/VotingEscrowDelegationProxy) | 0     | {                                                                                   | BIP-637    |   N/A    |
|               |                                                                                                          |       |   "delegation": [                                                                   |            |          |
|               |                                                                                                          |       |     "0x1702067424096F07A60e62cceE3dE9420068492D (20230525-l2-veboost-v2/VeBoostV2)" |            |          |
|               |                                                                                                          |       |   ]                                                                                 |            |          |
|               |                                                                                                          |       | }                                                                                   |            |          |
+---------------+----------------------------------------------------------------------------------------------------------+-------+-------------------------------------------------------------------------------------+------------+----------+
```
