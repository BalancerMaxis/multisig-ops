
## Mainnet DAO Multisig

[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/66b17461-8676-4794-9973-bfcbace9bd25)

[Sign Nonce 257](https://app.safe.global/transactions/queue?safe=eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)


FILENAME: `BIPs/00batched/2024-W39/1-0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f.json`
MULTISIG: `multisigs/dao (mainnet:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)`
COMMIT: `41c437668367f160cb00e7144e518c08003c81c4`
CHAIN(S): `mainnet`
TENDERLY: [`🟩 SUCCESS`](https://www.tdly.co/shared/simulation/de4a2ce0-ca58-4882-89c5-6dac54cd7521)

```
+----------+-------------------------------------------------+-----------------------------------------------------------------------------+----------------------------------------+---------+----------+
| function | token_symbol                                    | recipient                                                                   | amount                                 |   bip   | tx_index |
+----------+-------------------------------------------------+-----------------------------------------------------------------------------+----------------------------------------+---------+----------+
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/beets_service_provider:0x811912c19eEF91b9Dc3cA52fc426590cFB84FC86 | 90000.0 (RAW: 90000000000)             | BIP-632 |    0     |
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/beets_service_provider:0x811912c19eEF91b9Dc3cA52fc426590cFB84FC86 | 87000.0 (RAW: 87000000000)             | BIP-631 |    1     |
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/maxi_ops:0x166f54F44F271407f24AA1BE415a730035637325               | 398135.0 (RAW: 398135000000)           | BIP-694 |    2     |
| transfer | BAL:0xba100000625a3754423978a60c9317c58a424e3D  | multisigs/maxi_ops:0x166f54F44F271407f24AA1BE415a730035637325               | 32738.0 (RAW: 32738000000000000000000) | BIP-694 |    3     |
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/foundation_opco:0x3B8910F378034FD6E103Df958863e5c684072693        | 333325.0 (RAW: 333325000000)           | BIP-695 |    5     |
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/bizdev:0xC7E84373FC63A17B5B22EBaF86219141B630cD7a                 | 72000.0 (RAW: 72000000000)             | BIP-697 |    6     |
| transfer | BAL:0xba100000625a3754423978a60c9317c58a424e3D  | multisigs/bizdev:0xC7E84373FC63A17B5B22EBaF86219141B630cD7a                 | 6780.0 (RAW: 6780000000000000000000)   | BIP-697 |    7     |
+----------+-------------------------------------------------+-----------------------------------------------------------------------------+----------------------------------------+---------+----------+
```
```
+---------------+-----------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+-------------+---------------+---------+----------+
| function      | entrypoint                                                                                                      | target                                                                                             | selector    | parsed_inputs |   bip   | tx_index |
+---------------+-----------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+-------------+---------------+---------+----------+
| performAction | 0xf5dECDB1f3d1ee384908Fbe16D2F0348AE43a9eA (20221124-authorizer-adaptor-entrypoint/AuthorizerAdaptorEntrypoint) | 0xed0bb13496ce24EFFF8f9734A9707D092d4Be10c (root_gauges/50GOLD/25WETH/25USDC-base-root-ed0b)       | killGauge() |               | BIP-686 |    8     |
| performAction | 0xf5dECDB1f3d1ee384908Fbe16D2F0348AE43a9eA (20221124-authorizer-adaptor-entrypoint/AuthorizerAdaptorEntrypoint) | 0xbf8F01EbCf0A21C46D23ADa2C86EB31c9965B2F0 (root_gauges/GOLD/BAL/USDC-base-root-bf8f)              | killGauge() |               | BIP-686 |    9     |
| performAction | 0xf5dECDB1f3d1ee384908Fbe16D2F0348AE43a9eA (20221124-authorizer-adaptor-entrypoint/AuthorizerAdaptorEntrypoint) | 0xA8d4b31225BD6FAF1363DB5A0AB6c016894985d1 (root_gauges/50GOLD-25USDC-25WSTETH-arbitrum-root-a8d4) | killGauge() |               | BIP-686 |    10    |
| performAction | 0xf5dECDB1f3d1ee384908Fbe16D2F0348AE43a9eA (20221124-authorizer-adaptor-entrypoint/AuthorizerAdaptorEntrypoint) | 0x86Cf58bD7A64f2304227d1a490660D2954dB4a91 (root_gauges/GOLD-BAL-AURA-wstETH-arbitrum-root-86cf)   | killGauge() |               | BIP-686 |    11    |
+---------------+-----------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+-------------+---------------+---------+----------+
```
```
+-------------+-------------------------------------------------------------------------------+-------+----------------------------------------------------------------------------------+------------+----------+
| fx_name     | to                                                                            | value | inputs                                                                           | bip_number | tx_index |
+-------------+-------------------------------------------------------------------------------+-------+----------------------------------------------------------------------------------+------------+----------+
| retrieve    | 0x0e2d46fe246eb926d939A10efA96fB7d4EB14bB3 (aave/balancer_stk_aave_retrieval) | 0     | {}                                                                               | BIP-689    |   N/A    |
| withdraw    | 0x4f8AD938eBA0CD19155a835f617317a6E788c868 (tokens/Locked GNO)                | 0     | {                                                                                | BIP-696    |   N/A    |
|             |                                                                               |       |   "amount": [                                                                    |            |          |
|             |                                                                               |       |     "raw:9051000000000000000000, 18 decimals:9051, 6 decimals: 9051000000000000" |            |          |
|             |                                                                               |       |   ]                                                                              |            |          |
|             |                                                                               |       | }                                                                                |            |          |
| approve     | 0x6810e776880C02933D47DB1b9fc05908e5386b96 (tokens/GNO)                       | 0     | {                                                                                | BIP-696    |   N/A    |
|             |                                                                               |       |   "_spender": [                                                                  |            |          |
|             |                                                                               |       |     "0x88ad09518695c6c3712AC10a214bE5109a655671 (gnosis/omnibridge)"             |            |          |
|             |                                                                               |       |   ],                                                                             |            |          |
|             |                                                                               |       |   "_value": [                                                                    |            |          |
|             |                                                                               |       |     "raw:9051000000000000000000, 18 decimals:9051, 6 decimals: 9051000000000000" |            |          |
|             |                                                                               |       |   ]                                                                              |            |          |
|             |                                                                               |       | }                                                                                |            |          |
| relayTokens | 0x88ad09518695c6c3712AC10a214bE5109a655671 (gnosis/omnibridge)                | 0     | {                                                                                | BIP-696    |   N/A    |
|             |                                                                               |       |   "token": [                                                                     |            |          |
|             |                                                                               |       |     "0x6810e776880C02933D47DB1b9fc05908e5386b96 (tokens/GNO)"                    |            |          |
|             |                                                                               |       |   ],                                                                             |            |          |
|             |                                                                               |       |   "_receiver": [                                                                 |            |          |
|             |                                                                               |       |     "0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89 (multisigs/karpatkey)"           |            |          |
|             |                                                                               |       |   ],                                                                             |            |          |
|             |                                                                               |       |   "_value": [                                                                    |            |          |
|             |                                                                               |       |     "raw:9051000000000000000000, 18 decimals:9051, 6 decimals: 9051000000000000" |            |          |
|             |                                                                               |       |   ]                                                                              |            |          |
|             |                                                                               |       | }                                                                                |            |          |
+-------------+-------------------------------------------------------------------------------+-------+----------------------------------------------------------------------------------+------------+----------+
```

## Karpatkey Managed Treasury (mainnet)
[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/ebd5ade9-fd7e-4291-b93d-45b3c1441bc5)

[Sign Nonce 49](https://app.safe.global/transactions/queue?safe=eth:0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89)

FILENAME: `BIPs/00batched/2024-W39/1-0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89.json`
MULTISIG: `multisigs/karpatkey (mainnet:0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89)`
COMMIT: `41c437668367f160cb00e7144e518c08003c81c4`
CHAIN(S): `mainnet`
TENDERLY: [`🟩 SUCCESS`](https://www.tdly.co/shared/simulation/37831e1a-03c8-4984-a440-24dd6790759b)

```
+-----------+------------------------------------------------------------------+-------+----------------------------------------------------------------------+------------+----------+
| fx_name   | to                                                               | value | inputs                                                               | bip_number | tx_index |
+-----------+------------------------------------------------------------------+-------+----------------------------------------------------------------------+------------+----------+
| swapOwner | 0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89 (multisigs/karpatkey) | 0     | {                                                                    | BIP-688    |   N/A    |
|           |                                                                  |       |   "prevOwner": [                                                     |            |          |
|           |                                                                  |       |     "0x823DF0278e4998cD0D06FB857fBD51e85b18A250 (EOA/dao/nanexcool)" |            |          |
|           |                                                                  |       |   ],                                                                 |            |          |
|           |                                                                  |       |   "oldOwner": [                                                      |            |          |
|           |                                                                  |       |     "0x478eC43c6867c2884f87B21c164f1fD1308bD9a3 (EOA/dao/trentmc0)"  |            |          |
|           |                                                                  |       |   ],                                                                 |            |          |
|           |                                                                  |       |   "newOwner": [                                                      |            |          |
|           |                                                                  |       |     "0x11761c7b08287d9489CD84C04DF6852F5C07107b (EOA/maxis/gosuto)"  |            |          |
|           |                                                                  |       |   ]                                                                  |            |          |
|           |                                                                  |       | }                                                                    |            |          |
+-----------+------------------------------------------------------------------+-------+----------------------------------------------------------------------+------------+----------+
```

## Karpatkey Managed Treasury (gnosis)
[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/667ee645-c324-4de6-b05b-e910f2524df7)

[Sign Nonce 13](https://app.safe.global/transactions/queue?safe=gno:0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89)
FILENAME: `BIPs/00batched/2024-W39/100-0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89.json`
MULTISIG: `multisigs/karpatkey (gnosis:0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89)`
COMMIT: `41c437668367f160cb00e7144e518c08003c81c4`
CHAIN(S): `gnosis`
TENDERLY: [`🟩 SUCCESS`](https://www.tdly.co/shared/simulation/8385c146-7ba6-40a0-95e4-8e4e85480af9)

```
+-------------+------------------------------------------------------------------+-------+-------------------------------------------------------------------------------+------------+----------+
| fx_name     | to                                                               | value | inputs                                                                        | bip_number | tx_index |
+-------------+------------------------------------------------------------------+-------+-------------------------------------------------------------------------------+------------+----------+
| removeOwner | 0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89 (multisigs/karpatkey) | 0     | {                                                                             | BIP-696    |   N/A    |
|             |                                                                  |       |   "prevOwner": [                                                              |            |          |
|             |                                                                  |       |     "0xA39a62304d8d43B35114ad7bd1258B0E50e139b3 (EOA/dao/eboadom)"            |            |          |
|             |                                                                  |       |   ],                                                                          |            |          |
|             |                                                                  |       |   "owner": [                                                                  |            |          |
|             |                                                                  |       |     "0x7f87c1C42BeF332245F8B3cCAdD8224541CDaEcE (EOA/karpatkey/balancer_eoa)" |            |          |
|             |                                                                  |       |   ],                                                                          |            |          |
|             |                                                                  |       |   "_threshold": [                                                             |            |          |
|             |                                                                  |       |     "6"                                                                       |            |          |
|             |                                                                  |       |   ]                                                                           |            |          |
|             |                                                                  |       | }                                                                             |            |          |
| swapOwner   | 0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89 (multisigs/karpatkey) | 0     | {                                                                             | BIP-688    |   N/A    |
|             |                                                                  |       |   "prevOwner": [                                                              |            |          |
|             |                                                                  |       |     "0x823DF0278e4998cD0D06FB857fBD51e85b18A250 (EOA/dao/nanexcool)"          |            |          |
|             |                                                                  |       |   ],                                                                          |            |          |
|             |                                                                  |       |   "oldOwner": [                                                               |            |          |
|             |                                                                  |       |     "0x478eC43c6867c2884f87B21c164f1fD1308bD9a3 (EOA/dao/trentmc0)"           |            |          |
|             |                                                                  |       |   ],                                                                          |            |          |
|             |                                                                  |       |   "newOwner": [                                                               |            |          |
|             |                                                                  |       |     "0x11761c7b08287d9489CD84C04DF6852F5C07107b (EOA/maxis/gosuto)"           |            |          |
|             |                                                                  |       |   ]                                                                           |            |          |
|             |                                                                  |       | }                                                                             |            |          |
+-------------+------------------------------------------------------------------+-------+-------------------------------------------------------------------------------+------------+----------+
```
