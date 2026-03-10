# [BIP-916] Set Network Remapping Manager for StakeDAO

## Motivation

StakeDAO is launching their OnlyBoost strategies, which optimally allocate boost between StakeDAO and Aura on sidechains (Base and Arbitrum initially). To enable cross-chain boost for their veBAL position, the StakeDAO multisig needs to be designated as the `NetworkRemappingManager` for their veBAL locker on the [VotingEscrowRemapper](https://etherscan.io/address/0x83e443ef4f9963c77bd860f94500075556668cb8) contract. This grants StakeDAO the ability to call `setNetworkRemapping`, allowing them to manage their own L2 boost addresses.

This follows the same procedure as [BIP-341](https://forum.balancer.fi/t/bip-341-enable-tetu-cross-chain-boost/5007), which enabled cross-chain boost for Tetu.

## Specification

The DAO Multisig `0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f` will execute a single transaction batch on **Ethereum mainnet**:

1. **Grant permission**: Call `grantRole` on the Authorizer (`0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6`) with:
   - `role`: `0x6bb341db03eede206e544c654a59ef89eea83bc65fada2cfeeaf18c5c0f76ac0` — the action ID for `setNetworkRemappingManager` on the VotingEscrowRemapper ([verifiable here](https://github.com/balancer/balancer-deployments/blob/912cfaebda16d3b26a7bd931ce663ee8e44285f0/action-ids/mainnet/action-ids.json#L1340))
   - `account`: `0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f` (DAO Multisig)

2. **Set remapping manager**: Call `setNetworkRemappingManager` on the VotingEscrowRemapper (`0x83E443EF4f9963C77bd860f94500075556668cb8`) with:
   - `localUser`: `0xea79d1A83Da6DB43a85942767C389fE0ACf336A5` (StakeDAO veBAL locker)
   - `delegate`: `0xB0552b6860CE5C0202976Db056b5e3Cc4f9CC765` (StakeDAO multisig)

3. **Revoke permission**: Call `revokeRole` on the Authorizer to remove the `setNetworkRemappingManager` permission from the DAO Multisig.

## Risk Assessment

Low risk. The permission is granted and revoked atomically within the same transaction batch, so the DAO Multisig never retains the elevated permission beyond execution. The `setNetworkRemappingManager` function only designates who can manage L2 boost remappings for a specific veBAL locker — it does not grant access to any funds.
