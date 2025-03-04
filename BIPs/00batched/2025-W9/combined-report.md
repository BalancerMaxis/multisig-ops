# Ethereum DAO Multisig

[Tenderly]()

[Sign nonce 265](https://app.safe.global/transactions/queue?safe=eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)

```
+----------+-------------------------------------------------+------------------------------------------------------------------------+----------------------------+---------+----------+
| function | token_symbol                                    | recipient                                                              | amount                     |   bip   | tx_index |
+----------+-------------------------------------------------+------------------------------------------------------------------------+----------------------------+---------+----------+
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/foundation_opco:0x3B8910F378034FD6E103Df958863e5c684072693   | 35200.0 (RAW: 35200000000) | BIP-786 |    0     |
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | payees/hypernative_payments:0x5CA24e2A586834A7B96216D68b26A82405e3DC15 | 80000.0 (RAW: 80000000000) | BIP-775 |    3     |
+----------+-------------------------------------------------+------------------------------------------------------------------------+----------------------------+---------+----------+
```

```
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name         | caller_address                             | fx_paths                                                                                                | action_ids                                                         |   bip   | tx_index |
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250121-v3-stable-surge/StablePool/startAmplificationParameterUpdate(uint256,uint256)                  | 0x3050dfbb6294dc29c5cae13acb241fddea61d345d9b8c809f216c8259b013ff8 | BIP-787 |    0     |
|                       |                     |                                            | 20250121-v3-stable-surge/StablePool/stopAmplificationParameterUpdate()                                  | 0x866d7d17a9b007d202e4da84f38a0bfbb310db8184a4f1d2e6de3c8e78ecd1e0 |         |          |
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250121-v3-stable-surge/StableSurgeHook/setMaxSurgeFeePercentage(address,uint256)                      | 0x2f27aa67b6bf44b4441ea2656c22e09252261845a98dc577a6fc06b6526f8bcc | BIP-778 |    2     |
|                       |                     |                                            | 20250121-v3-stable-surge/StableSurgeHook/setSurgeThresholdPercentage(address,uint256)                   | 0x66c657ea0d5ce1dc0286795937131c61620bb6ccd0f126fbfe3799d8b89a9753 |         |          |
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250117-v3-contract-registry/BalancerContractRegistry/addOrUpdateBalancerContractAlias(string,address) | 0xc50be693f82453d6b7fbfabf52ae750e168eb530ce663aec7b2fe1c96cfdf381 | BIP-790 |    3     |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/deprecateBalancerContract(address)               | 0xda5605d0e7c70ae825d1d2e45f0656490960542c725946cd5532909f723501b4 |         |          |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/deregisterBalancerContract(string)               | 0x534d9f0ca09366b50105b12a7492e9429c8621cf57c845195e7c6874fa413d03 |         |          |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/registerBalancerContract(uint8,string,address)   | 0xf539cbe9be426b500591a2dd63970d37952d95006d1039f35e731b4b52b33e73 |         |          |
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```

# Gnosis DAO Multisig

[Tenderly]()

[Sign nonce 29](https://app.safe.global/transactions/queue?safe=gno:0x2a5AEcE0bb9EfFD7608213AE1745873385515c18)

```
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name         | caller_address                             | fx_paths                                                                                                | action_ids                                                         |   bip   | tx_index |
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250121-v3-stable-surge/StablePool/startAmplificationParameterUpdate(uint256,uint256)                  | 0x4acf55e494b685b95a5b14cf8c5507d75bd1aa71a85fc1214c0e8b825a469170 | BIP-787 |    0     |
|                       |                     |                                            | 20250121-v3-stable-surge/StablePool/stopAmplificationParameterUpdate()                                  | 0x472cb2d86bd228ad5c01dda464760927533d1f2075d5857fb2c01bfee9790125 |         |          |
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250121-v3-stable-surge/StableSurgeHook/setMaxSurgeFeePercentage(address,uint256)                      | 0x7380cab0ed6c5f6a40913d98c4931ae4d29a059fa33ae27635ab1f4f6e4c5077 | BIP-778 |    1     |
|                       |                     |                                            | 20250121-v3-stable-surge/StableSurgeHook/setSurgeThresholdPercentage(address,uint256)                   | 0x4fdd01a86430670b9ac98e6baa39e03b7df692fb1c7c988b41fa7d510f8ff7e7 |         |          |
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250117-v3-contract-registry/BalancerContractRegistry/addOrUpdateBalancerContractAlias(string,address) | 0x96933475aa135d9d02d175e3f20f420fb65595ebeade476edf970dd5fddda874 | BIP-790 |    2     |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/deprecateBalancerContract(address)               | 0xdb3b99d52cd97741d98d8cf58982c82a1c7caee958ed94e5fcf909ba57ef27bc |         |          |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/deregisterBalancerContract(string)               | 0xa2ccd901b5d57e951d23051ad0a49e4127722628b5f0318468fae768fd6e4a02 |         |          |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/registerBalancerContract(uint8,string,address)   | 0xd7b567352ab1dc8647c52f123cd411b5b0d47dbd5a4c5a65d799d675cc6604f2 |         |          |
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```

# Base DAO Multisig

[Tenderly]()

[Sign nonce 11](https://app.safe.global/transactions/queue?safe=base:0xC40DCFB13651e64C8551007aa57F9260827B6462)

```
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name         | caller_address                             | fx_paths                                                                                                | action_ids                                                         |   bip   | tx_index |
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250121-v3-stable-surge/StableSurgeHook/setMaxSurgeFeePercentage(address,uint256)                      | 0xe81edd4ccc5901443972e580b5d997ced38f33bd4f7e9bca8829dc5efcca6fed | BIP-778 |    0     |
|                       |                     |                                            | 20250121-v3-stable-surge/StableSurgeHook/setSurgeThresholdPercentage(address,uint256)                   | 0x4a7d099f7d634af69cf552b5b1c76ed8d44074051cbca5a59b842154288b96f1 |         |          |
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250121-v3-stable-surge/StablePool/startAmplificationParameterUpdate(uint256,uint256)                  | 0xbf865f1c6f8d104fabfc55638d1622f92901741c27314f329670c51b54f3eded | BIP-787 |    1     |
|                       |                     |                                            | 20250121-v3-stable-surge/StablePool/stopAmplificationParameterUpdate()                                  | 0x1a357d5b1643481255960a2981adcdd96069c98aff413a5e8387d5e199d34a64 |         |          |
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250117-v3-contract-registry/BalancerContractRegistry/addOrUpdateBalancerContractAlias(string,address) | 0x0918fe18bf5dd7146d6ef70b2bc468e01847a23ebc248c46f0f3e860e760b95a | BIP-790 |    2     |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/deprecateBalancerContract(address)               | 0x4f36a3d4a5722964e73c1331cfbe74b0ce2717c92b0cb39e4e1bb402a34ce490 |         |          |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/deregisterBalancerContract(string)               | 0xff6339cb1834d4fd03de1defb693e9bdbaf87b32c6ef785e9c1e9306a13e0991 |         |          |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/registerBalancerContract(uint8,string,address)   | 0x6c32ca35628dd90c860faff8e24fa89e8ccb7546536eefc8365ceceb013efad1 |         |          |
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250212-v3-mev-capture-hook/MevCaptureHook/addMevTaxExemptSenders(address[])                           | 0x17024432bfda7b943932633322c0dcc89b380311f26a3544ccda6eb5cd6bef65 | BIP-789 |    3     |
|                       |                     |                                            | 20250212-v3-mev-capture-hook/MevCaptureHook/removeMevTaxExemptSenders(address[])                        | 0x2fcebd2fe4f213bb084e9d41e9b8a1ceb8b2d2916ff032c93f556deb984a9ff6 |         |          |
|                       |                     |                                            | 20250212-v3-mev-capture-hook/MevCaptureHook/disableMevTax()                                             | 0xbda3401247f7a4661e06d58b77fb710e3531091c0b521d24a744f58933745e18 |         |          |
|                       |                     |                                            | 20250212-v3-mev-capture-hook/MevCaptureHook/enableMevTax()                                              | 0xfb223c0dc293c599b2e25e2e5a94f569741ec76e268779a3e2326ab5b41daed0 |         |          |
|                       |                     |                                            | 20250212-v3-mev-capture-hook/MevCaptureHook/setDefaultMevTaxMultiplier(uint256)                         | 0x772cd983d0b4a8e717b61ba3beaaff7b352f1c220763e3ac36c91d7850d81edc |         |          |
|                       |                     |                                            | 20250212-v3-mev-capture-hook/MevCaptureHook/setDefaultMevTaxThreshold(uint256)                          | 0xa8ef455da97a35724b2fb844ad06e34b821bbc8df26a448eec44e9dedd96bfe9 |         |          |
|                       |                     |                                            | 20250212-v3-mev-capture-hook/MevCaptureHook/setMaxMevSwapFeePercentage(uint256)                         | 0x89ca43e71ae2fb8e3f4752bca2af32b2423de7071aa88e76302aa11910ecea32 |         |          |
|                       |                     |                                            | 20250212-v3-mev-capture-hook/MevCaptureHook/setPoolMevTaxMultiplier(address,uint256)                    | 0xe8f2291394946ee5c5f23ca57ef6f232e07bf6c66fe01c5f2adfc012dde326fd |         |          |
|                       |                     |                                            | 20250212-v3-mev-capture-hook/MevCaptureHook/setPoolMevTaxThreshold(address,uint256)                     | 0x235aeae017d90d17ad71f80bcff4fed15fff4c242382e58f8fe01dad43a8d585 |         |          |
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```

# Arbitrum DAO Multisig

[Tenderly]()

[Sign nonce 48](https://app.safe.global/transactions/queue?safe=arb1:0xaF23DC5983230E9eEAf93280e312e57539D098D0)

```
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name         | caller_address                             | fx_paths                                                                                                | action_ids                                                         |   bip   | tx_index |
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250121-v3-stable-surge/StableSurgeHook/setMaxSurgeFeePercentage(address,uint256)                      | 0x261258d23af1013ceb3a0574a5f194e3d4d09a07c0b9014665519c3f1b37f792 | BIP-778 |    0     |
|                       |                     |                                            | 20250121-v3-stable-surge/StableSurgeHook/setSurgeThresholdPercentage(address,uint256)                   | 0x5968f4b1f98171ccadc78df4f25cf8262b250f2f12a83c45b7311b4674d23e0a |         |          |
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250117-v3-contract-registry/BalancerContractRegistry/addOrUpdateBalancerContractAlias(string,address) | 0x86f7150372eac1ea58a41e472ce008974af1af41c17a9d2b75dd1eb608f7f1e1 | BIP-790 |    1     |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/deprecateBalancerContract(address)               | 0xcd03479a888f646243549839f3e3e0a8541e4fadd747050ce030b54ae2e3f3ea |         |          |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/deregisterBalancerContract(string)               | 0x35d64fe29e697ddb438d402a641010dac7cf88c9c2f8609d657125377d3554a0 |         |          |
|                       |                     |                                            | 20250117-v3-contract-registry/BalancerContractRegistry/registerBalancerContract(uint8,string,address)   | 0xd222e876fa09fc854125c959257507aa6ad490d65a8b94721974e7cc8953f739 |         |          |
| Authorizer/grantRoles | multisigs/maxi_omni | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250121-v3-stable-surge/StablePool/startAmplificationParameterUpdate(uint256,uint256)                  | 0x2fbb47746d921903b9f91d439cf9e524a40a377607923d64f01c38c5d0ea1b14 | BIP-787 |    2     |
|                       |                     |                                            | 20250121-v3-stable-surge/StablePool/stopAmplificationParameterUpdate()                                  | 0xdecec4789661e9e43897955fb7d3796d8f5159ba0cc6593dbf71f88c8f4da475 |         |          |
+-----------------------+---------------------+--------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```
