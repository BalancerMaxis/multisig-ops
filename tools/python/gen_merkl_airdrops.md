# `gen_merkl_airdrops.md`

## Morpho

Repeat the following steps for each chain and/or reward token:

### Step 1: Grab and Sim Payload to Claim Rewards via Omni Msig

Click claim rewards button on the [Safe Ethereum app](https://app.safe.global/apps/open?safe=eth:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e&appUrl=https%3A%2F%2Fsafe-app.morpho.org) ([or for Base](https://app.safe.global/apps/open?safe=base:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e&appUrl=https://safe-app.morpho.org)) and grab the `data` argument of the `EthereumBundlerV2.multicall`.

Also run a sim of that tx. Grab the `value` of the `Transfer` event emitted by the reward token:

```
{
  "from": "0x330eefa8a787552dc5cad3c3ca644844b1e61ddb",
  "to": "0x9ff471f9f98f42e5151c7855fd1b5aa906b1af7e",
  "value": "931502544520041839881"
}
```

### Step 2: Configure Watchlist

If there are multiple pools sharing the same claimable amount, populate the `claimable` field of `gen_merkl_airdrops_watchlist.json` with the `value` from step 1 _but empty the `reward_wei` fields of each pool_. The script will populate these based on the USD split it calculates.

If there is only one pool that the rewards should be redistributed to, fill in the `reward_wei` field directly and leave `claimable` blank (`""`).

### Step 3: Determine User Shares

Run `python tools/python/gen_merkl_airdrops.py` and upload the airdrop json artifact to https://legacy.merkl.xyz/create/drop. Click `Preview Transaction` -> `Build a payload` -> `Download Safe Payload`.

### Step 4: Consolidate both Payloads

Create one final payload JSON that has the `multicall` transaction from step 1, followed by all the necessary campaign creations for that chain from step 3.

### Rename Final Payload and Upload

Rename final payload to `epoch_<#>-<protocol>-<chain_id>.json` and place in `MaxiOps/merkl/payloads/`.

## Merit

See instructions in the `gen_merkl_airdrops.py` comments in order to include a Merit cycle when running the script. Then impersonate the omni msig and capture the claim calldata on https://app.merkl.xyz/users/0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e. Convert the airdrop into a payload via the usual https://legacy.merkl.xyz/create/drop and append the relevant transactions to the claim payload.
