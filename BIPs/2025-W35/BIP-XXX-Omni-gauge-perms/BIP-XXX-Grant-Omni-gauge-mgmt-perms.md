# [BIP-XXX] Grant Universal Gauge Management Permissions

## Motivation

This BIP proposes to grant universal gauge management permissions to the Maxi Omni multisig to streamline gauge operations and reduce turnaround time for gauge management activities. Currently, gauge management operations require individual permission grants for specific functions, creating bottlenecks and delays in routine gauge maintenance and administration.

These permissions will remain under full DAO governance control. The Maxi Omni multisig will only execute gauge management actions following explicit DAO approval through snapshot votes. This proposal changes the execution multisig from individual permission grants to a streamlined execution model, while maintaining the requirement for DAO governance approval for all gauge management decisions.

By granting these execution permissions, the Balancer DAO can enable more efficient gauge operations while preserving the governance oversight and approval process through established DAO voting mechanisms.

## Gauge Management Permissions

The authorizer will grant the following permissions to **Maxi Omni** (`0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e`):

### Action ID Summary

| Function | Action ID | Description |
|----------|-----------|-------------|
| `GaugeAdder.addGauge(address,string)` | `0x83dc5eaaade2c71d34c71bd21fe617f5f6d83bf53bd9d886d00c756e386b8cd1` | Add new gauges to the system |
| `LiquidityGaugeV5.setRelativeWeightCap(uint256)` | `0xae60dce27f51ce5815357b9f6b40f200557867f8222262a1646c005d09b7dfba` | Set relative weight caps for gauges |
| `LiquidityGaugeV5.unkillGauge()` | `0x076e9815202aa39577192023cfa569d6504b003183b2bc13cd0046523dfa23ea` | Reactivate killed gauges |
| `LiquidityGaugeV5.killGauge()` | `0xec1d467d9ab03a0079c22a89037209f5763aec973897ea763e2cf25d71a5f12e` | Deactivate gauges |

### Detailed Action ID Mapping

- **20230519-gauge-adder-v4/GaugeAdder.addGauge(address,string)**
  - Action ID: `0x83dc5eaaade2c71d34c71bd21fe617f5f6d83bf53bd9d886d00c756e386b8cd1`
  - Function: Enable addition of new liquidity gauges

- **20220822-mainnet-gauge-factory-v2/LiquidityGaugeV5.setRelativeWeightCap(uint256)**
  - Action ID: `0xae60dce27f51ce5815357b9f6b40f200557867f8222262a1646c005d09b7dfba`
  - Function: Set maximum relative weight caps for gauge emissions

- **20220325-mainnet-gauge-factory/LiquidityGaugeV5.unkillGauge()**
  - Action ID: `0x076e9815202aa39577192023cfa569d6504b003183b2bc13cd0046523dfa23ea`
  - Function: Reactivate previously killed gauges to resume emissions

- **20220325-mainnet-gauge-factory/LiquidityGaugeV5.killGauge()**
  - Action ID: `0xec1d467d9ab03a0079c22a89037209f5763aec973897ea763e2cf25d71a5f12e`
  - Function: Deactivate gauges to stop emissions

## Technical Specification

The implementation will use the `grantRoles` function on the Balancer Authorizer to assign the specified action IDs to the Maxi Omni multisig address.

```
Target: Balancer Authorizer
Function: grantRoles
Grantee: 0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e (Maxi Omni)
Action IDs: 
  - 0x83dc5eaaade2c71d34c71bd21fe617f5f6d83bf53bd9d886d00c756e386b8cd1
  - 0xae60dce27f51ce5815357b9f6b40f200557867f8222262a1646c005d09b7dfba
  - 0x076e9815202aa39577192023cfa569d6504b003183b2bc13cd0046523dfa23ea
  - 0xec1d467d9ab03a0079c22a89037209f5763aec973897ea763e2cf25d71a5f12e
```

## Risk Assessment

These permissions grant the Maxi Omni multisig comprehensive control over gauge lifecycle management. The risk is mitigated by:

1. **Multi-signature requirement**: All actions require consensus from multiple signers
2. **Established governance**: The Maxi Omni multisig operates under established DAO governance frameworks. Any gauge management transaction needs a governance vote before being queued in the multi-sig.
3. **Transparency**: All transactions are publicly visible on-chain
4. **Reversibility**: The DAO retains the ability to revoke these permissions if needed

## Benefits

- **Reduced operational friction**: Eliminates the need for individual permission grants and involvement of the DAO multi-sig for routine gauge management
- **Faster response times**: Enables quicker responses to gauge-related issues and requests (days instead of weeks)
- **Operational efficiency**: Streamlines the gauge management workflow
- **Consistent management**: Provides unified approach to gauge lifecycle management
