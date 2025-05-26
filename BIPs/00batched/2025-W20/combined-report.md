# Ethereum DAO Multisig

[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/322967cf-655a-4487-98f8-df9b4f1be78c)

[Sign nonce 267](https://app.safe.global/transactions/tx?safe=eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f&id=multisig_0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f_0xecf940fc5dbf9c6c80719624c6c209ebe168ecf05bc18e158e2d8dd0c5e60521)

```
+----------+------------------------------------------------+------------------------------------------------------------------------------+---------------------------------------+---------+----------+
| function | token_symbol                                   | recipient                                                                    | amount                                |   bip   | tx_index |
+----------+------------------------------------------------+------------------------------------------------------------------------------+---------------------------------------+---------+----------+
| transfer | BAL:0xba100000625a3754423978a60c9317c58a424e3D | multisigs/alliance_program/rocket:0xb867EA3bBC909954d737019FEf5AB25dFDb38CB9 | 9587.0 (RAW: 9587000000000000000000)  | BIP-822 |    0     |
| transfer | BAL:0xba100000625a3754423978a60c9317c58a424e3D | payees/karpatkey_payments:0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C         | 2966.56 (RAW: 2966560000000000000000) | BIP-648 |    2     |
+----------+------------------------------------------------+------------------------------------------------------------------------------+---------------------------------------+---------+----------+
```

```
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name                                            | caller_address                             | fx_paths                                                                                                                         | action_ids                                                         |   bip   | tx_index |
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | multisigs/maxi_omni                                    | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250403-v3-stable-surge-hook-v2/StableSurgeHook/setMaxSurgeFeePercentage(address,uint256)                                       | 0xf38ecb07c88c5307ae7e207ff9f96c7707a6093a6abb7c5c61020119536cc236 | BIP-820 |    3     |
|                       |                                                        |                                            | 20250403-v3-stable-surge-hook-v2/StableSurgeHook/setSurgeThresholdPercentage(address,uint256)                                    | 0x2b49aa01d0b0251c5fa59f092390a988da3dbdc3609dc3c4bc36a4491da73681 |         |          |
| Authorizer/grantRoles | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper | 0x90BD26fbb9dB17D75b56E4cA3A4c438FA7C93694 | 20250214-v3-protocol-fee-controller-v2/ProtocolFeeController/withdrawProtocolFeesForToken(address,address,address)               | 0x9fe8e7d354d4d4c9b828af97a9fb461b79747eb597d1d1919127b884ed03a3df | BIP-821 |    4     |
| Authorizer/grantRoles | EOA/keepers/v3_fee_bot                                 | 0x74E283B985EA76c55C8B48d6bD1067a418188424 | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper/sweepProtocolFeesForToken(address,address,uint256,uint256,address)        | 0x948915f00181e892799c0395cd771a3e2799fa1b93083824be21aabd4aa8f344 | BIP-821 |    5     |
|                       |                                                        |                                            | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper/sweepProtocolFeesForWrappedToken(address,address,uint256,uint256,address) | 0x00d2a3463fdb96359d21e38b6b564b93a1b869bbb3cbaa1c73510d0b103659d6 |         |          |
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```

```
+------------------+-----------------------------------------------------------------------------------------------+-------+--------------------------------------------------------------------------------------+------------+----------+
| fx_name          | to                                                                                            | value | inputs                                                                               | bip_number | tx_index |
+------------------+-----------------------------------------------------------------------------------------------+-------+--------------------------------------------------------------------------------------+------------+----------+
| allowlistAddress | 0x7869296Efd0a76872fEE62A058C8fBca5c1c826C (20220420-smart-wallet-checker/SmartWalletChecker) | 0     | {                                                                                    | BIP-822    |   N/A    |
|                  |                                                                                               |       |   "contractAddress": [                                                               |            |          |
|                  |                                                                                               |       |     "0xb867EA3bBC909954d737019FEf5AB25dFDb38CB9 (multisigs/alliance_program/rocket)" |            |          |
|                  |                                                                                               |       |   ]                                                                                  |            |          |
|                  |                                                                                               |       | }                                                                                    |            |          |
+------------------+-----------------------------------------------------------------------------------------------+-------+--------------------------------------------------------------------------------------+------------+----------+
```

# Ethereum Karpatkey Managed Multisig

[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/40b06a15-8052-41f6-9048-c4b4bf9c8a6f)

[Sign nonce 56](https://app.safe.global/transactions/queue?safe=eth:0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89)

```
+----------+-------------------------------------------------+----------------------------------------------------------------------+----------------------------+---------+----------+
| function | token_symbol                                    | recipient                                                            | amount                     |   bip   | tx_index |
+----------+-------------------------------------------------+----------------------------------------------------------------------+----------------------------+---------+----------+
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | payees/karpatkey_payments:0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C | 46233.0 (RAW: 46233000000) | BIP-013 |    0     |
+----------+-------------------------------------------------+----------------------------------------------------------------------+----------------------------+---------+----------+
```

# Gnosis DAO Multisig

[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/ab63e055-6929-4f5a-b0ae-7dbb87f67e58)

[Sign nonce 31](https://app.safe.global/transactions/tx?safe=gno:0x2a5AEcE0bb9EfFD7608213AE1745873385515c18&id=multisig_0x2a5AEcE0bb9EfFD7608213AE1745873385515c18_0x30b2ad3afe568e652fc1dab400cec5a1a600b321416c87755e00562b8d6646b6)

```
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name                                            | caller_address                             | fx_paths                                                                                                                         | action_ids                                                         |   bip   | tx_index |
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper | 0x5939ab16fDf1991B0EF603c639B6b501A7841fAB | 20250214-v3-protocol-fee-controller-v2/ProtocolFeeController/withdrawProtocolFeesForToken(address,address,address)               | 0x7c0fa8c5add2fab51cc64b00dc8278f6829e8235e9ac804973fc336736b88ba6 | BIP-821 |    0     |
| Authorizer/grantRoles | EOA/keepers/v3_fee_bot                                 | 0x74E283B985EA76c55C8B48d6bD1067a418188424 | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper/sweepProtocolFeesForToken(address,address,uint256,uint256,address)        | 0xf911142df6f3dafb994647846e9ec22da65353bb5db6eb21ea5e8769b4a4bf60 | BIP-821 |    1     |
|                       |                                                        |                                            | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper/sweepProtocolFeesForWrappedToken(address,address,uint256,uint256,address) | 0xe66dd2e0c1746dd77ff830176ddae9b55e66c03d29d6213649befd14219e0533 |         |          |
| Authorizer/grantRoles | multisigs/maxi_omni                                    | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250403-v3-stable-surge-hook-v2/StableSurgeHook/setMaxSurgeFeePercentage(address,uint256)                                       | 0x6648ca4015a562c4110635d0f2f8f402af08c32926b73b04307f778a4662ea47 | BIP-820 |    2     |
|                       |                                                        |                                            | 20250403-v3-stable-surge-hook-v2/StableSurgeHook/setSurgeThresholdPercentage(address,uint256)                                    | 0xa9902a51b5285acf6244965666f9096d34561241355f4bd05e099f319fe8fde1 |         |          |
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```

# Arbitrum DAO Multisig

[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/647fc90d-0cfa-4db0-a5f7-d0679de42475)

[Sign nonce 50](https://app.safe.global/transactions/tx?safe=arb1:0xaF23DC5983230E9eEAf93280e312e57539D098D0&id=multisig_0xaF23DC5983230E9eEAf93280e312e57539D098D0_0xc9c3640fb1a2409e14874afa0ef4f68452ee83a6c46073319c437b90eb650079)

```
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name                                            | caller_address                             | fx_paths                                                                                                                         | action_ids                                                         |   bip   | tx_index |
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper | 0x136f1EFcC3f8f88516B9E94110D56FDBfB1778d1 | 20250214-v3-protocol-fee-controller-v2/ProtocolFeeController/withdrawProtocolFeesForToken(address,address,address)               | 0x610537725ddaed423abcb2b23d9191781b990fceb0f445f4bfe56f049514ff4c | BIP-821 |    0     |
| Authorizer/grantRoles | EOA/keepers/v3_fee_bot                                 | 0x74E283B985EA76c55C8B48d6bD1067a418188424 | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper/sweepProtocolFeesForToken(address,address,uint256,uint256,address)        | 0x14063ceb23c91467860eb9a242020a95c50c929fb1f9b7a3f8df15f0a0c4df70 | BIP-821 |    1     |
|                       |                                                        |                                            | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper/sweepProtocolFeesForWrappedToken(address,address,uint256,uint256,address) | 0xe804beeda244417d4f174b615090e88cd0ade3ba64e3307cd01cedf9306ee16c |         |          |
| Authorizer/grantRoles | multisigs/maxi_omni                                    | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250403-v3-stable-surge-hook-v2/StableSurgeHook/setMaxSurgeFeePercentage(address,uint256)                                       | 0x7ed51e972f7682e8a513e8d697daf6179714308b17bffd3d972a34a8a86fe107 | BIP-820 |    2     |
|                       |                                                        |                                            | 20250403-v3-stable-surge-hook-v2/StableSurgeHook/setSurgeThresholdPercentage(address,uint256)                                    | 0x3e5b3786c2433c83d82d4d118259a3cf5b7dd26b4f21c6c56115c2ce1cfa825b |         |          |
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```

# Avalanche DAO Multisig

[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/dc6a195c-036d-4206-850c-11d0bc457f7f)

[Sign nonce 24](https://app.safe.global/transactions/tx?safe=avax:0x17b11FF13e2d7bAb2648182dFD1f1cfa0E4C7cf3&id=multisig_0x17b11FF13e2d7bAb2648182dFD1f1cfa0E4C7cf3_0x6f9283cf92c2be4eabdb1f8f5acc5f3df91c37cbeb3f9446e324eb6739c3dfec)

```
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name                                            | caller_address                             | fx_paths                                                                                                                         | action_ids                                                         |   bip   | tx_index |
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper | 0xB9d01CA61b9C181dA1051bFDd28e1097e920AB14 | 20250214-v3-protocol-fee-controller-v2/ProtocolFeeController/withdrawProtocolFeesForToken(address,address,address)               | 0xd92d29a05f2748c0b17d7df988dd0a9d2d957f8651a7209ff5f6e8901b60b53f | BIP-821 |    0     |
| Authorizer/grantRoles | EOA/keepers/v3_fee_bot                                 | 0x74E283B985EA76c55C8B48d6bD1067a418188424 | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper/sweepProtocolFeesForToken(address,address,uint256,uint256,address)        | 0x56bec12b93b41e25525d94ad33219973ebd07435c70d646ed8de38740b32b062 | BIP-821 |    1     |
|                       |                                                        |                                            | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper/sweepProtocolFeesForWrappedToken(address,address,uint256,uint256,address) | 0xb00c6b1b735e7187175763c9d5ca79c75662399946b352289e53d53cadbc750e |         |          |
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```

# Base DAO Multisig

[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/b96157d7-a42f-4e61-b104-479a548e9ae4)

[Sign nonce 13](https://app.safe.global/transactions/tx?safe=base:0xC40DCFB13651e64C8551007aa57F9260827B6462&id=multisig_0xC40DCFB13651e64C8551007aa57F9260827B6462_0xb062c5abae5ea2902fae174f9198d4cc23ad6901dbfd58f23284f1990d09de59)

```
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| function              | caller_name                                            | caller_address                             | fx_paths                                                                                                                         | action_ids                                                         |   bip   | tx_index |
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
| Authorizer/grantRoles | multisigs/maxi_omni                                    | 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e | 20250403-v3-stable-surge-hook-v2/StableSurgeHook/setMaxSurgeFeePercentage(address,uint256)                                       | 0x01ef05374c39f0094ff2f8278f21a14a89ed025e8564c7a541d4f26ed9bd23fd | BIP-820 |    0     |
|                       |                                                        |                                            | 20250403-v3-stable-surge-hook-v2/StableSurgeHook/setSurgeThresholdPercentage(address,uint256)                                    | 0xccde3eb1bbf6269f3b1ff650d0e3bf089ad0a119c82f5e48db9761d64a346c77 |         |          |
| Authorizer/grantRoles | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper | 0xe2fa4e1d17725e72dcdAfe943Ecf45dF4B9E285b | 20250214-v3-protocol-fee-controller-v2/ProtocolFeeController/withdrawProtocolFeesForToken(address,address,address)               | 0x0ef595d0eed0a6e5adfc1fe810c72ad3d4b23e7c0d66a74fd4799e2f799af0bf | BIP-821 |    1     |
| Authorizer/grantRoles | EOA/keepers/v3_fee_bot                                 | 0x74E283B985EA76c55C8B48d6bD1067a418188424 | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper/sweepProtocolFeesForToken(address,address,uint256,uint256,address)        | 0x80168541b21bdc5c250801e99d4c9c179e9da35e17449e2b2fd8815b60b4e111 | BIP-821 |    2     |
|                       |                                                        |                                            | 20250503-v3-protocol-fee-sweeper-v2/ProtocolFeeSweeper/sweepProtocolFeesForWrappedToken(address,address,uint256,uint256,address) | 0x1b341058d98047825a630f3e1ae601c4c74c54bca28c97974e1fad86957910f9 |         |          |
+-----------------------+--------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+---------+----------+
```
