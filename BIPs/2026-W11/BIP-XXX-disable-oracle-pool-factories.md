# [BIP-XXX]: Disable Outdated Oracle LP Pool Factories (v1 and v2)

## Summary

This proposal requests the DAO multisig to disable outdated Oracle LP Pool Factories across all networks where they are deployed. This includes both the v1 (deprecated) and the original v2 (overwritten) versions of the `WeightedLPOracleFactory` and `StableLPOracleFactory` contracts.

## Motivation

As requested by BLabs, all outdated Oracle Pool Factories for v1 need to be disabled. The original v2 factories were never fully rolled out and have since been overwritten with updated deployments following Certora audit suggestions. While the old v2 contracts are no longer listed in the deployments repo, they still exist on-chain and should be disabled for completeness.

All factory addresses referenced in this BIP correspond to [commit `9a29caf`](https://github.com/balancer/balancer-deployments/blob/9a29caf63cc6bfad564a84e33e8f912c180054b9/addresses/mainnet.json) of `balancer-deployments`, which is the last commit before the v2 overwrite.

These payloads must go through the DAO multisig because the `disable()` permissions for these factories were never granted to any operator or the Omnisig.

## Factories to Disable

### V1 Factories (Deprecated)

| Deployment Task | Contract |
|---|---|
| [`20250814-v3-weighted-pool-oracle`](https://github.com/balancer/balancer-deployments/blob/master/tasks/20250814-v3-weighted-pool-oracle) | `WeightedLPOracleFactory` |
| [`20250815-v3-stable-pool-oracle`](https://github.com/balancer/balancer-deployments/blob/master/tasks/20250815-v3-stable-pool-oracle) | `StableLPOracleFactory` |

### V2 Factories (Overwritten, no longer in deployments repo)

| Deployment Task | Contract |
|---|---|
| [`20260202-v3-weighted-pool-oracle-v2`](https://github.com/balancer/balancer-deployments/blob/9a29caf63cc6bfad564a84e33e8f912c180054b9/addresses/mainnet.json#L2064) | `WeightedLPOracleFactory` |
| [`20260203-v3-stable-pool-oracle-v2`](https://github.com/balancer/balancer-deployments/blob/9a29caf63cc6bfad564a84e33e8f912c180054b9/addresses/mainnet.json#L2078) | `StableLPOracleFactory` |

## Affected Networks and Factory Addresses

### Mainnet (Chain ID: 1)

| Factory | Address |
|---|---|
| WeightedLPOracleFactory v1 | `0x05503B3aDE04aCA81c8D6F88eCB73Ba156982D2B` |
| StableLPOracleFactory v1 | `0x83bf399FA3DC49Af8fb5c34031a50c7C93F56129` |
| WeightedLPOracleFactory v2 | `0xDd10aDF05379D7C0Ee4bC9c72ecc5C01c40E25b8` |
| StableLPOracleFactory v2 | `0x99f2D91EBA577e4Bf7175E72B3Ef2B6dDb1FaBe3` |

### Arbitrum (Chain ID: 42161)

| Factory | Address |
|---|---|
| WeightedLPOracleFactory v1 | `0x7f4C133e44381D05129F9B81bAD8Fa9F3345D29B` |
| StableLPOracleFactory v1 | `0x816e90DC85bF016455017a76Bc09CC0451Eeb308` |
| WeightedLPOracleFactory v2 | `0xA9AEeB57Efe61338C0d07f3e5Bb82519C4Ad1103` |
| StableLPOracleFactory v2 | `0xa59F164d6cf6ee5d63580C0bcEA5CCB2e50b908c` |

### Optimism (Chain ID: 10)

| Factory | Address |
|---|---|
| WeightedLPOracleFactory v1 | `0x6eE18fbb1BBcC5CF700cD75ea1aef2bb21e3cB3F` |
| StableLPOracleFactory v1 | `0xb96524227c4B5Ab908FC3d42005FE3B07abA40E9` |
| WeightedLPOracleFactory v2 | `0xEB2BB012869255f8C622563Dc4C3AFA8619fe804` |
| StableLPOracleFactory v2 | `0xC4c4940DC7c57DF46d3A217647dB1649721Cf468` |

### Gnosis (Chain ID: 100)

| Factory | Address |
|---|---|
| WeightedLPOracleFactory v1 | `0x8A8B9f35765899B3a0291700141470D79EA2eA88` |
| StableLPOracleFactory v1 | `0xbF94192c652183c0f50056417f4D04810329f12c` |
| WeightedLPOracleFactory v2 | `0x332694Ef46D880DF6Ea9593e04CB8ABEE5F81D99` |
| StableLPOracleFactory v2 | `0x4eFcd8bcE8AC9b94bd76648e2c85bEf6c40F3228` |

### Avalanche (Chain ID: 43114)

| Factory | Address |
|---|---|
| WeightedLPOracleFactory v1 | `0x0E800D8d2E8b4694610AEdc385Aa6D763492B106` |
| StableLPOracleFactory v1 | `0x4eff2d77D9fFbAeFB4b141A3e494c085b3FF4Cb5` |
| WeightedLPOracleFactory v2 | `0x9958317b80ee5f10457017d54c2484D722059157` |
| StableLPOracleFactory v2 | `0x5939ab16fDf1991B0EF603c639B6b501A7841fAB` |

### Base (Chain ID: 8453)

| Factory | Address |
|---|---|
| WeightedLPOracleFactory v1 | `0x774cB66e2B2dB59A9daF175e9b2B7A142E17EB94` |
| StableLPOracleFactory v1 | `0xb21A277466e7dB6934556a1Ce12eb3F032815c8A` |
| WeightedLPOracleFactory v2 | `0x9958317b80ee5f10457017d54c2484D722059157` |
| StableLPOracleFactory v2 | `0x5939ab16fDf1991B0EF603c639B6b501A7841fAB` |

## Technical Specification

For each factory on each network, the DAO multisig executes a 3-step transaction pattern via the Authorizer:

1. **`grantRole(actionId, daoMultisig)`** on the Authorizer -- grants the DAO multisig the `disable()` role for the target factory
2. **`disable()`** on the factory -- permanently disables the factory, preventing new pool creation
3. **`revokeRole(actionId, daoMultisig)`** on the Authorizer -- revokes the role so the DAO multisig does not retain unnecessary permissions

Each network payload contains 12 transactions (4 factories x 3 steps).

### Authorizer Addresses

| Network | Authorizer |
|---|---|
| Mainnet, Arbitrum, Optimism, Gnosis, Avalanche | `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` |
| Base | `0x809B79b53F18E9bc08A961ED4678B901aC93213a` |

### V2 Action IDs (disable())

V1 action IDs can be looked up from the [balancer-deployments action-ids](https://github.com/balancer/balancer-deployments/tree/master/action-ids). The overwritten v2 factory action IDs are no longer in the repo and were queried on-chain via `getActionId(bytes4)`:

| Network | WeightedLPOracleFactory v2 | StableLPOracleFactory v2 |
|---|---|---|
| Mainnet | `0xaad0e51c18069fb241bf8179dc6c7d583e506dd672ef9a85ef122dd000deba76` | `0xb3c9c0ec52436494a8f6527a835a3442d43fb2d4268c638d9e8f670a5546afe8` |
| Arbitrum | `0x32cfd519f4e04a2d3b88e1e667811368433ec3da01605dbc26d85a8d54dc834b` | `0x249bc3c0021e108ccf28b9f7934b423928be80b8c823bab8254edba17b359ea4` |
| Optimism | `0x92b93830f0497ce935614ceb53508d12d772244a34a0bbbeab832a4c824f0b90` | `0xfc212a18b66df1a184af12c3a698e2f1b55a002fa96e4ad2e37ddd708f99723a` |
| Gnosis | `0x5a2389555953f58e8746cb8c3171904d268fce2d55fa1aac3f20343ccd04cb0b` | `0x315b841cfaf795ea83cbe267847195f6fdba4a7a9f5ed870c28d9e4d4b145e28` |
| Avalanche | `0x0f19a8e265e66504de04b28811bb8fba950087dc6ab21a23e5d757937d4c38c8` | `0xd6ef2cdea6236fe8b350fe1371523aade37cb3ec44de40e46a13ac44ab467e9e` |
| Base | `0x0f19a8e265e66504de04b28811bb8fba950087dc6ab21a23e5d757937d4c38c8` | `0xd6ef2cdea6236fe8b350fe1371523aade37cb3ec44de40e46a13ac44ab467e9e` |