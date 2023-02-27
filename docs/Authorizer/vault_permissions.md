## Realyer permissions context for the Balancer V2 Vault


### Why Relayers?
[Realyers](https://docs.balancer.fi/concepts/advanced/relayers.html) allow users to enable modular automations to asset in executing complex functions agains the vault.

Beyond the migration example listed, here are some other cases in which relayers have been mentioned in governance:

- [Nested join, exits and swaps](https://forum.balancer.fi/t/proposal-authorize-the-batch-relayer/2378): Allow more diverse joining/exit from pools with a single user transaction.
- [Trading through boosted pools](https://forum.balancer.fi/t/proposal-polygon-authorize-batch-relayer-v2-for-usd-boosted-pool/2655)
- [Single TX deposit and stake](https://forum.balancer.fi/t/bip-31-authorize-the-batch-relayer-v3/3488)
- [Reaper integration for beets](https://forum.balancer.fi/t/bip-70-authorize-the-batch-relayer-v4/3734)


### How do permissions work / double authorization

For each of the functions listed below, the vault has special handling configured for double authorization.  This means that in order for the an address to call commands in this context on a users behalf, the following 2 conditions must be true: 

1. The address listed has been granted access to the function called via the Authorizer.
2. The user has granted the specific address the ability to act on their behalf by calling [setRealyerApproval](https://github.com/balancer-labs/balancer-v2-monorepo/blob/63ffcf2018b02c038041540e4984bc6dd4a8c89c/pkg/vault/contracts/VaultAuthorization.sol#L96) on the vault for the given relayer.

[VaultAuthorization.sol](https://github.com/balancer-labs/balancer-v2-monorepo/blob/master/pkg/vault/contracts/VaultAuthorization.sol) contains enough of the code to get a good idea how the double auth function works.

### List of vault function selectors in the special Authroizer Permisisons Context

- manageUserBalance : Utilize existing Vault allowances and internal balances so that a user does not have to re-approve the new relayer for each token.
- joinPool : Add liquidity to a pool on the user’s behalf.
- exitPool : Remove liquidity from a pool on the user’s behalf.
- swap : Trade within a single pool on the user’s behalf.
- batchSwap : Make a multihop trade or source liquidity from multiple pools.
- setRelayerApproval : Approve another relayer on the user’s behalf ([user must still provide a signed message](https://github.com/balancer-labs/balancer-v2-monorepo/blob/63ffcf2018b02c038041540e4984bc6dd4a8c89c/pkg/vault/contracts/VaultAuthorization.sol#L96)).

Because of heavy space optimizations in the vault source code, it is not obvious that these are the calls that participate in this context at glance. A third party review of the code that revealed this context better would make a nice Balancer Grant.