# [BIP-XXX] Grant Emergency subDAO Missing v3 Pool Factory Disable Permissions

### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/XXXX

### Motivation 
With Balancer v3 deployed across multiple networks (mainnet, arbitrum, gnosis, base), various pool factory types have been launched but the emergency subDAO is missing critical disable permissions for some v3 pool factories. In case of a potential malfunction or security issue, the emergency subDAO needs the ability to disable these factories immediately. 

After cross-checking existing permissions against required v3 factory disable permissions, the following missing permissions have been identified and need to be granted to the respective emergency subDAO wallets:

#### Emergency DAO Missing Permissions

**Mainnet - Missing 1 Permission:**
- `StableSurgePoolFactory.disable`

**Arbitrum - Missing 3 Permissions:**
- `Gyro2CLPPoolFactory.disable`
- `StablePoolFactory.disable` 
- `StableSurgePoolFactory.disable`

**Gnosis - Missing 3 Permissions:**
- `Gyro2CLPPoolFactory.disable`
- `StablePoolFactory.disable`
- `StableSurgePoolFactory.disable`

**Base - Missing 3 Permissions:**
- `Gyro2CLPPoolFactory.disable`
- `StablePoolFactory.disable`
- `StableSurgePoolFactory.disable`

#### Action ID Summary Table

| Network | Emergency Safe | Missing Action IDs |
| :---- | :---- | :---- |
| Mainnet | 0xA29F61256e948F3FB707b4b3B138C5cCb9EF9888 | 0x125f8185b9efebee1266720f09cd756bd130f70cb24b5929efa8ff3df158e86f |
| Arbitrum | 0xf404C5a0c02397f0908A3524fc5eb84e68Bbe60D | 0x8962b605c4877aadeecae387492d3bc0bfb2f52c30aa0633200cf1e8c3238f3c, 0x54d04f96e1384dacfbc4bb06d4876678ad3ba07c255782bd693bc9df4b367e24, 0xfdae18cb216aeaa8c8bfbb7a875699bd6b0e7d31cc28292a26a182860745d00c |
| Gnosis | 0xd6110A7756080a4e3BCF4e7EBBCA8E8aDFBC9962 | 0x7949fb1573bd2626186b70a6d475351a5f6effad72cd82900248d5a3308c0f64, 0x3a974164b03a634d51c05b0322775609d8e50216de1c030b3840bbc63a2228a4, 0x0186b98b0b37d1c06787083bcf5c4b408e784a4eb2469478a76c94678d925933 |
| Base | 0x183C55A0dc7A7Da0f3581997e764D85Fd9E9f63a | 0xac0d1be9ff7d3e69a1596ff43dec0fa65eb1ffb47dafc81433455b3f5014370f, 0x28e9e31c7abbe803f2c44dde4b6b484e671a6ee8ced3402269274f6064ab48b4, 0x72a5df2a33143829e209d8720489edacfae688c4df61120a45ae57de8907b8b6 |

#### Detailed Action ID Mapping

**Mainnet:**
- StableSurgePoolFactory.disable: `0x125f8185b9efebee1266720f09cd756bd130f70cb24b5929efa8ff3df158e86f` ([20250121-v3-stable-surge](https://github.com/balancer/balancer-deployments/blob/master/action-ids/mainnet/action-ids.json))

**Arbitrum:**
- Gyro2CLPPoolFactory.disable: `0x8962b605c4877aadeecae387492d3bc0bfb2f52c30aa0633200cf1e8c3238f3c` ([20250120-v3-gyro-2clp](https://github.com/balancer/balancer-deployments/blob/master/action-ids/arbitrum/action-ids.json))
- StablePoolFactory.disable: `0x54d04f96e1384dacfbc4bb06d4876678ad3ba07c255782bd693bc9df4b367e24` ([20250324-v3-stable-pool](https://github.com/balancer/balancer-deployments/blob/master/action-ids/arbitrum/action-ids.json))
- StableSurgePoolFactory.disable: `0xfdae18cb216aeaa8c8bfbb7a875699bd6b0e7d31cc28292a26a182860745d00c` ([20250404-v3-stable-surge](https://github.com/balancer/balancer-deployments/blob/master/action-ids/arbitrum/action-ids.json))

**Gnosis:**
- Gyro2CLPPoolFactory.disable: `0x7949fb1573bd2626186b70a6d475351a5f6effad72cd82900248d5a3308c0f64` ([20250120-v3-gyro-2clp](https://github.com/balancer/balancer-deployments/blob/master/action-ids/gnosis/action-ids.json))
- StablePoolFactory.disable: `0x3a974164b03a634d51c05b0322775609d8e50216de1c030b3840bbc63a2228a4` ([20250324-v3-stable-pool](https://github.com/balancer/balancer-deployments/blob/master/action-ids/gnosis/action-ids.json))
- StableSurgePoolFactory.disable: `0x0186b98b0b37d1c06787083bcf5c4b408e784a4eb2469478a76c94678d925933` ([20250404-v3-stable-surge](https://github.com/balancer/balancer-deployments/blob/master/action-ids/gnosis/action-ids.json))

**Base:**
- Gyro2CLPPoolFactory.disable: `0xac0d1be9ff7d3e69a1596ff43dec0fa65eb1ffb47dafc81433455b3f5014370f` ([20250120-v3-gyro-2clp](https://github.com/balancer/balancer-deployments/blob/master/action-ids/base/action-ids.json))
- StablePoolFactory.disable: `0x28e9e31c7abbe803f2c44dde4b6b484e671a6ee8ced3402269274f6064ab48b4` ([20250324-v3-stable-pool](https://github.com/balancer/balancer-deployments/blob/master/action-ids/base/action-ids.json))
- StableSurgePoolFactory.disable: `0x72a5df2a33143829e209d8720489edacfae688c4df61120a45ae57de8907b8b6` ([20250404-v3-stable-surge](https://github.com/balancer/balancer-deployments/blob/master/action-ids/base/action-ids.json))

**Note:** Avalanche, Optimism, and Hyperevm already have all required emergency permissions and do not require additional payloads.

## Technical Specifications

The DAO multisig on each network will interact with the Authorizer by calling `grantRoles`, with `roles` as an array of the corresponding action IDs mentioned in the table above and `account` as the Emergency subDAO safe.

### Verification

The current permissions can be verified by checking the active permissions files:
- [Mainnet permissions](https://github.com/BalancerMaxis/bal_addresses/blob/main/outputs/permissions/active/mainnet.json)
- [Arbitrum permissions](https://github.com/BalancerMaxis/bal_addresses/blob/main/outputs/permissions/active/arbitrum.json)
- [Gnosis permissions](https://github.com/BalancerMaxis/bal_addresses/blob/main/outputs/permissions/active/gnosis.json)
- [Base permissions](https://github.com/BalancerMaxis/bal_addresses/blob/main/outputs/permissions/active/base.json)

The action IDs can be verified by checking the respective network's action-ids.json files in the [balancer-deployments repository](https://github.com/balancer/balancer-deployments/tree/master/action-ids).
