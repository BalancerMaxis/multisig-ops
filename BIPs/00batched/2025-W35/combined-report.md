# Combined Payload Report - 2025-W35

## Ethereum: `multisigs/dao`

```
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name         | caller_address                             | fx_paths                                                                                      | action_ids                                                         |   bip   | tx_index |
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | multisigs/emergency | 0xA29F61256e948F3FB707b4b3B138C5cCb9EF9888 | 20250121-v3-stable-surge/StableSurgePoolFactory/disable()                                     | 0x125f8185b9efebee1266720f09cd756bd130f70cb24b5929efa8ff3df158e86f | BIP-865 |    0     |
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20230519-gauge-adder-v4/GaugeAdder/addGauge(address,string)                                   | 0x83dc5eaaade2c71d34c71bd21fe617f5f6d83bf53bd9d886d00c756e386b8cd1 | BIP-867 |    1     |
|                       |                     |                                            | 20220823-arbitrum-root-gauge-factory-v2/ArbitrumRootGauge/setRelativeWeightCap(uint256)       | 0xae60dce27f51ce5815357b9f6b40f200557867f8222262a1646c005d09b7dfba |         |          |
|                       |                     |                                            | 20220823-polygon-root-gauge-factory-v2/PolygonRootGauge/setRelativeWeightCap(uint256)         | 0x076e9815202aa39577192023cfa569d6504b003183b2bc13cd0046523dfa23ea |         |          |
|                       |                     |                                            | 20230217-gnosis-root-gauge-factory/GnosisRootGauge/setRelativeWeightCap(uint256)              | 0xec1d467d9ab03a0079c22a89037209f5763aec973897ea763e2cf25d71a5f12e |         |          |
|                       |                     |                                            | 20230215-single-recipient-gauge-factory-v2/SingleRecipientGauge/setRelativeWeightCap(uint256) | 0x2960d085c4c968d7cad55c0da3f97014525b948fdce990ecaef4e832b5f0b151 |         |          |
|                       |                     |                                            | 20220822-mainnet-gauge-factory-v2/LiquidityGaugeV5/setRelativeWeightCap(uint256)              | 0x3f44776af02a9227991da37715b44e45db40735e216b3ab33144859bb6737166 |         |          |
|                       |                     |                                            | 20220823-optimism-root-gauge-factory-v2/OptimismRootGauge/setRelativeWeightCap(uint256)       |                                                                    |         |          |
|                       |                     |                                            | 20230911-base-root-gauge-factory/BaseRootGauge/setRelativeWeightCap(uint256)                  |                                                                    |         |          |
|                       |                     |                                            | 20240522-fraxtal-root-gauge-factory/OptimisticRootGauge/setRelativeWeightCap(uint256)         |                                                                    |         |          |
|                       |                     |                                            | 20230526-zkevm-root-gauge-factory/PolygonZkEVMRootGauge/setRelativeWeightCap(uint256)         |                                                                    |         |          |
|                       |                     |                                            | 20230811-avalanche-root-gauge-factory-v2/AvalancheRootGauge/setRelativeWeightCap(uint256)     |                                                                    |         |          |
|                       |                     |                                            | 20230529-avalanche-root-gauge-factory/AvalancheRootGauge/setRelativeWeightCap(uint256)        |                                                                    |         |          |
|                       |                     |                                            | 20220823-polygon-root-gauge-factory-v2/PolygonRootGauge/unkillGauge()                         |                                                                    |         |          |
|                       |                     |                                            | 20220325-mainnet-gauge-factory/LiquidityGaugeV5/unkillGauge()                                 |                                                                    |         |          |
|                       |                     |                                            | 20220413-arbitrum-root-gauge-factory/ArbitrumRootGauge/unkillGauge()                          |                                                                    |         |          |
|                       |                     |                                            | 20220823-optimism-root-gauge-factory-v2/OptimismRootGauge/unkillGauge()                       |                                                                    |         |          |
|                       |                     |                                            | 20220413-polygon-root-gauge-factory/PolygonRootGauge/unkillGauge()                            |                                                                    |         |          |
|                       |                     |                                            | 20230526-zkevm-root-gauge-factory/PolygonZkEVMRootGauge/unkillGauge()                         |                                                                    |         |          |
|                       |                     |                                            | 20230217-gnosis-root-gauge-factory/GnosisRootGauge/unkillGauge()                              |                                                                    |         |          |
|                       |                     |                                            | 20220628-optimism-root-gauge-factory/OptimismRootGauge/unkillGauge()                          |                                                                    |         |          |
|                       |                     |                                            | 20240522-fraxtal-root-gauge-factory/OptimisticRootGauge/unkillGauge()                         |                                                                    |         |          |
|                       |                     |                                            | 20230529-avalanche-root-gauge-factory/AvalancheRootGauge/unkillGauge()                        |                                                                    |         |          |
|                       |                     |                                            | 20220823-arbitrum-root-gauge-factory-v2/ArbitrumRootGauge/unkillGauge()                       |                                                                    |         |          |
|                       |                     |                                            | 20230811-avalanche-root-gauge-factory-v2/AvalancheRootGauge/unkillGauge()                     |                                                                    |         |          |
|                       |                     |                                            | 20220822-mainnet-gauge-factory-v2/LiquidityGaugeV5/unkillGauge()                              |                                                                    |         |          |
|                       |                     |                                            | 20220325-single-recipient-gauge-factory/SingleRecipientGauge/unkillGauge()                    |                                                                    |         |          |
|                       |                     |                                            | 20230215-single-recipient-gauge-factory-v2/SingleRecipientGauge/unkillGauge()                 |                                                                    |         |          |
|                       |                     |                                            | 20230911-base-root-gauge-factory/BaseRootGauge/unkillGauge()                                  |                                                                    |         |          |
|                       |                     |                                            | 20220823-optimism-root-gauge-factory-v2/OptimismRootGauge/killGauge()                         |                                                                    |         |          |
|                       |                     |                                            | 20230526-zkevm-root-gauge-factory/PolygonZkEVMRootGauge/killGauge()                           |                                                                    |         |          |
|                       |                     |                                            | 20220413-arbitrum-root-gauge-factory/ArbitrumRootGauge/killGauge()                            |                                                                    |         |          |
|                       |                     |                                            | 20230811-avalanche-root-gauge-factory-v2/AvalancheRootGauge/killGauge()                       |                                                                    |         |          |
|                       |                     |                                            | 20230911-base-root-gauge-factory/BaseRootGauge/killGauge()                                    |                                                                    |         |          |
|                       |                     |                                            | 20220413-polygon-root-gauge-factory/PolygonRootGauge/killGauge()                              |                                                                    |         |          |
|                       |                     |                                            | 20220823-arbitrum-root-gauge-factory-v2/ArbitrumRootGauge/killGauge()                         |                                                                    |         |          |
|                       |                     |                                            | 20230217-gnosis-root-gauge-factory/GnosisRootGauge/killGauge()                                |                                                                    |         |          |
|                       |                     |                                            | 20230529-avalanche-root-gauge-factory/AvalancheRootGauge/killGauge()                          |                                                                    |         |          |
|                       |                     |                                            | 20220325-single-recipient-gauge-factory/SingleRecipientGauge/killGauge()                      |                                                                    |         |          |
|                       |                     |                                            | 20220823-polygon-root-gauge-factory-v2/PolygonRootGauge/killGauge()                           |                                                                    |         |          |
|                       |                     |                                            | 20220628-optimism-root-gauge-factory/OptimismRootGauge/killGauge()                            |                                                                    |         |          |
|                       |                     |                                            | 20230215-single-recipient-gauge-factory-v2/SingleRecipientGauge/killGauge()                   |                                                                    |         |          |
|                       |                     |                                            | 20220822-mainnet-gauge-factory-v2/LiquidityGaugeV5/killGauge()                                |                                                                    |         |          |
|                       |                     |                                            | 20220325-mainnet-gauge-factory/LiquidityGaugeV5/killGauge()                                   |                                                                    |         |          |
|                       |                     |                                            | 20240522-fraxtal-root-gauge-factory/OptimisticRootGauge/killGauge()                           |                                                                    |         |          |
|                       |                     |                                            | 20230519-gauge-adder-v4/GaugeAdder/addGaugeType(string)                                       |                                                                    |         |          |
|                       |                     |                                            | 20230519-gauge-adder-v4/GaugeAdder/setGaugeFactory(address,string)                            |                                                                    |         |          |
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```

## Optimism: `multisigs/dao`

```
+----------+---------------------------------------------------------+----------------------------------------------------------------+--------------------------------------------------+---------+----------+
| function | token_symbol                                            | recipient                                                      | amount                                           |   bip   | tx_index |
+----------+---------------------------------------------------------+----------------------------------------------------------------+--------------------------------------------------+---------+----------+
| transfer | USDC:0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85         | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 32982.95 (RAW: 32982950000)                      | BIP-850 |    0     |
| transfer | OP:0x4200000000000000000000000000000000000042           | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 80114.01456134167 (RAW: 80114014561341671912269) | BIP-850 |    1     |
| transfer | BAL:0xFE8B128bA8C78aabC59d4c64cEE7fF28e9379921          | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 1083.21485649496 (RAW: 1083214856494960031532)   | BIP-850 |    2     |
| transfer | USDC:0x7F5c764cBc14f9669B88837ca1490cCa17c31607         | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 25719.0 (RAW: 25719000000)                       | BIP-850 |    3     |
| transfer | 80BAL-20WETH:0xc38C2fC871188935B9C615e73B17f2e7e463C8b1 | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 8363.938598298697 (RAW: 8363938598298696554545)  | BIP-850 |    4     |
+----------+---------------------------------------------------------+----------------------------------------------------------------+--------------------------------------------------+---------+----------+
```

## Gnosis: `multisigs/dao`

```
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name         | caller_address                             | fx_paths                                                  | action_ids                                                         |   bip   | tx_index |
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | multisigs/emergency | 0xd6110A7756080a4e3BCF4e7EBBCA8E8aDFBC9962 | 20250120-v3-gyro-2clp/Gyro2CLPPoolFactory/disable()       | 0x7949fb1573bd2626186b70a6d475351a5f6effad72cd82900248d5a3308c0f64 | BIP-865 |    0     |
|                       |                     |                                            | 20250324-v3-stable-pool-v2/StablePoolFactory/disable()    | 0x3a974164b03a634d51c05b0322775609d8e50216de1c030b3840bbc63a2228a4 |         |          |
|                       |                     |                                            | 20250121-v3-stable-surge/StableSurgePoolFactory/disable() | 0x0186b98b0b37d1c06787083bcf5c4b408e784a4eb2469478a76c94678d925933 |         |          |
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```

## Polygon: `multisigs/dao`

```
+----------+-------------------------------------------------+----------------------------------------------------------------+----------------------------------------------+---------+----------+
| function | token_symbol                                    | recipient                                                      | amount                                       |   bip   | tx_index |
+----------+-------------------------------------------------+----------------------------------------------------------------+----------------------------------------------+---------+----------+
| transfer | USDT:0xc2132D05D31c914a87C6611C10748AEb04B58e8F | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 1166.300485 (RAW: 1166300485)                | BIP-850 |    0     |
| transfer | USDC:0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359 | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 2429.685603 (RAW: 2429685603)                | BIP-850 |    1     |
| transfer | USDC:0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 10150.743919 (RAW: 10150743919)              | BIP-850 |    2     |
| transfer | WETH:0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619 | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 0.003743179747701364 (RAW: 3743179747701364) | BIP-850 |    3     |
+----------+-------------------------------------------------+----------------------------------------------------------------+----------------------------------------------+---------+----------+
```

```
+----------+-----------------------------------------------------------+-------+------------------------------------------------------------------------+------------+----------+
| fx_name  | to                                                        | value | inputs                                                                 | bip_number | tx_index |
+----------+-----------------------------------------------------------+-------+------------------------------------------------------------------------+------------+----------+
| withdraw | 0x794a61358D6845594F94dc1DB02A252b5b4814aD (aave/pool_v3) | 0     | {                                                                      | BIP-850    |   N/A    |
|          |                                                           |       |   "asset": [                                                           |            |          |
|          |                                                           |       |     "0x9a71012B13CA4d3D0Cdc72A177DF3ef03b0E76A3 (tokens/BAL)"          |            |          |
|          |                                                           |       |   ],                                                                   |            |          |
|          |                                                           |       |   "amount": [type(uint256).max]                                        |            |          |
|          |                                                           |       |   "to": [                                                              |            |          |
|          |                                                           |       |     "0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e (multisigs/maxi_omni)" |            |          |
|          |                                                           |       |   ]                                                                    |            |          |
|          |                                                           |       | }                                                                      |            |          |
+----------+-----------------------------------------------------------+-------+------------------------------------------------------------------------+------------+----------+
```

## Arbitrum: `multisigs/kpk_managed`

```
+----------+---------------------------------------------------------+-------+----------------------------------------------------------------------------+------------+----------+
| fx_name  | to                                                      | value | inputs                                                                     | bip_number | tx_index |
+----------+---------------------------------------------------------+-------+----------------------------------------------------------------------------+------------+----------+
| delegate | 0x912CE59144191C1204E64559FE8253a0e49E6548 (tokens/ARB) | 0     | {                                                                          | BIP-850    |   N/A    |
|          |                                                         |       |   "delegatee": [                                                           |            |          |
|          |                                                         |       |     "0x583E3EDc26E1B8620341bce90547197bfE2c1ddD (karpatkey/delegate_msig)" |            |          |
|          |                                                         |       |   ]                                                                        |            |          |
|          |                                                         |       | }                                                                          |            |          |
+----------+---------------------------------------------------------+-------+----------------------------------------------------------------------------+------------+----------+
```

## Arbitrum: `multisigs/dao`

```
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name         | caller_address                             | fx_paths                                                  | action_ids                                                         |   bip   | tx_index |
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | multisigs/emergency | 0xf404C5a0c02397f0908A3524fc5eb84e68Bbe60D | 20250120-v3-gyro-2clp/Gyro2CLPPoolFactory/disable()       | 0x8962b605c4877aadeecae387492d3bc0bfb2f52c30aa0633200cf1e8c3238f3c | BIP-865 |    0     |
|                       |                     |                                            | 20250324-v3-stable-pool-v2/StablePoolFactory/disable()    | 0x54d04f96e1384dacfbc4bb06d4876678ad3ba07c255782bd693bc9df4b367e24 |         |          |
|                       |                     |                                            | 20250121-v3-stable-surge/StableSurgePoolFactory/disable() | 0xfdae18cb216aeaa8c8bfbb7a875699bd6b0e7d31cc28292a26a182860745d00c |         |          |
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```

## Avalanche: `multisigs/dao`

```
+----------+----------------------------------------------------------+----------------------------------------------------------------+---------------------------------------------------+---------+----------+
| function | token_symbol                                             | recipient                                                      | amount                                            |   bip   | tx_index |
+----------+----------------------------------------------------------+----------------------------------------------------------------+---------------------------------------------------+---------+----------+
| transfer | 80BAL/20WAVAX:0xA39d8651689c8b6e5a9e0AA4362629aeF2c58F55 | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 18779.056320131607 (RAW: 18779056320131607397610) | BIP-850 |    0     |
| transfer | USDC:0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E          | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 3440.688438 (RAW: 3440688438)                     | BIP-850 |    1     |
| transfer | USDt:0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7          | multisigs/maxi_omni:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 65.719115 (RAW: 65719115)                         | BIP-850 |    2     |
+----------+----------------------------------------------------------+----------------------------------------------------------------+---------------------------------------------------+---------+----------+
```

## Base: `multisigs/dao`

```
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name         | caller_address                             | fx_paths                                                  | action_ids                                                         |   bip   | tx_index |
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | multisigs/emergency | 0x183C55A0dc7A7Da0f3581997e764D85Fd9E9f63a | 20250120-v3-gyro-2clp/Gyro2CLPPoolFactory/disable()       | 0xac0d1be9ff7d3e69a1596ff43dec0fa65eb1ffb47dafc81433455b3f5014370f | BIP-865 |    0     |
|                       |                     |                                            | 20250324-v3-stable-pool-v2/StablePoolFactory/disable()    | 0x28e9e31c7abbe803f2c44dde4b6b484e671a6ee8ced3402269274f6064ab48b4 |         |          |
|                       |                     |                                            | 20250121-v3-stable-surge/StableSurgePoolFactory/disable() | 0x72a5df2a33143829e209d8720489edacfae688c4df61120a45ae57de8907b8b6 |         |          |
+-----------------------+---------------------+--------------------------------------------+-----------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```
