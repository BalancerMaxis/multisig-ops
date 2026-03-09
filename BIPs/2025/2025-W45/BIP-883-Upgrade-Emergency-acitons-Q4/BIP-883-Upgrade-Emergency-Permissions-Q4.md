# [BIP-XXX] Emergency Safe Governance Improvements Q4 2025

## PR with Payload
tbd

# Summary

This proposal implements two critical improvements to the Balancer emergency safe system following a comprehensive security review by the Security Council in Madrid. The changes include: (1) reducing the emergency safe signer threshold from 4/7 to 3/7 to enable faster response times during critical incidents, and (2) revoking the `VaultAdmin.disableQueryPermanently()` permission from all emergency safes across all chains to eliminate unnecessary security risk.

## Introduction

During the Security Council meeting in Madrid, the team conducted a thorough review of the current emergency safe setup across all Balancer deployments. This review identified two areas for improvement that would enhance both the operational efficiency and security posture of the protocol's emergency response capabilities.

The emergency safes play a critical role in protecting the protocol and user funds during security incidents. These changes are designed to optimize the balance between quick emergency response and maintaining robust security controls.

## Motivation

### 1. Signer Threshold Reduction (4/7 → 3/7)

The current 4/7 threshold requirement for emergency safe actions creates potential delays during critical security incidents when rapid response is essential. In emergency situations where every minute counts, the additional coordination overhead of requiring four signers can significantly impact response time.

Key considerations:
- A 3/7 threshold still maintains strong security with majority agreement required
- Improves operational flexibility during time-sensitive emergencies
- Aligns with industry best practices for emergency multisig configurations
- Reduces the risk of being unable to act quickly when multiple signers are unavailable

### 2. Removal of `VaultAdmin.disableQueryPermanently()` Permission

The `VaultAdmin.disableQueryPermanently()` function presents an unnecessary security risk to the protocol. This permission allows for the permanent disabling of vault queries, which:
- Is not required for any legitimate emergency response scenario
- Could be misused to permanently impact protocol functionality if a signer key were compromised
- Represents a "foot gun" capability that provides no operational benefit
- Creates unnecessary surface area for potential security incidents

By removing this permission, we reduce the blast radius of potential emergency safe key compromises while maintaining all necessary emergency response capabilities.

## Technical Specification

The proposal includes two distinct operational changes:

#### Change 1: Safe Threshold Adjustment
The emergency safe signer threshold will be reduced from 4/7 to 3/7 across all relevant chains. This change is executed via direct Safe configuration updates by the emergency safe owners. This change will be performed for all Emergency safes.

#### Change 2: Permission Revocation on chains with Balancer v3 deployments
The `VaultAdmin.disableQueryPermanently()` permission (Action ID: `0x6832812101826d0b63748615617865e97f09b944c344d3bbd7d50b5be617eb16`) will be revoked from emergency safes across all chains.

### Execution Details

The permission revocations will be executed by calling `revokeRoles` on the respective Authorizer contracts across all chains.

**Role Action ID to Revoke**: `0x6832812101826d0b63748615617865e97f09b944c344d3bbd7d50b5be617eb16`
**Function**: `VaultAdmin.disableQueryPermanently()`

| Chain | Executing Multisig | Target (Authorizer) | Emergency Safe (Losing Permission) |
|-------|-------------------|---------------------|-------------------------------------|
| Ethereum | DAO Multisig (`0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f`) | `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` | `0xA29F61256e948F3FB707b4b3B138C5cCb9EF9888` |
| Arbitrum | DAO Multisig (`0xaF23DC5983230E9eEAf93280e312e57539D098D0`) | `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` | `0xf404C5a0c02397f0908A3524fc5eb84e68Bbe60D` |
| Optimism | DAO Multisig (`0x043f9687842771b3dF8852c1E9801DCAeED3f6bc`) | `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` | `0xd4c87b33afcE39F1E3F4aF1ce8fFFF7241d9128B` |
| Avalanche | DAO Multisig (`0x17b11FF13e2d7bAb2648182dFD1f1cfa0E4C7cf3`) | `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` | `0x308f8d3536261C32c97D2f85ddc357f5cCdF33F0` |
| Base | DAO Multisig (`0xC40DCFB13651e64C8551007aa57F9260827B6462`) | `0x809B79b53F18E9bc08A961ED4678B901aC93213a` | `0x183C55A0dc7A7Da0f3581997e764D85Fd9E9f63a` |
| Gnosis | DAO Multisig (`0x2a5AEcE0bb9EfFD7608213AE1745873385515c18`) | `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` | `0xd6110A7756080a4e3BCF4e7EBBCA8E8aDFBC9962` |
| HyperEVM | Omni Multisig (`0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e`) | `0x85a80afee867aDf27B50BdB7b76DA70f1E853062` | `0x44613a28347206F5E26C1B8Db7Dc73f450219746` |
| Plasma | Omni Multisig (`0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e`) | `0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5` | `0x0d3319A8057A0C8afd87dFEEA252541A76d56Ebf` |

## Risk Assessment

### Benefits
- **Improved Emergency Response**: Faster coordination during critical security incidents
- **Reduced Security Surface**: Elimination of unnecessary and potentially dangerous permission
- **Maintained Security**: 3/7 threshold still requires majority consensus
- **Operational Efficiency**: More practical threshold that doesn't compromise security

### Risks and Mitigations
- **Lower Threshold Risk**: While 3/7 is lower than 4/7, it still requires a majority of signers and aligns with industry standards for emergency multisigs
- **Coordination Risk**: The remaining emergency permissions are all necessary and appropriate for emergency response
- **Reversibility**: The DAO retains the ability to adjust the threshold or restore permissions if needed through future governance

### Security Considerations
The emergency safes will maintain all necessary permissions for legitimate emergency actions including:
- Pausing pools and the vault during security incidents
- Enabling recovery mode on pools
- Disabling compromised pool factories
- Other time-critical protective actions

The removal of `disableQueryPermanently()` does not impact any of these critical capabilities.

## References

- Security Council Meeting Notes (Madrid, Q4 2025)
- [Balancer Deployments Repository](https://github.com/balancer/balancer-deployments)
- [Multisig Operations Repository](https://github.com/BalancerMaxis/multisig-ops)
- Payload Files: `BIPs/2025-W45/BIP-XXX-Upgrade-Emergency-acitons-Q4/`
