# `gen_merkl_airdrops.md`

## Morpho

### Step 1: Claim Rewards via Omni Msig

Either use claim rewards button on the [Safe app](https://app.safe.global/apps/open?safe=eth:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e&appUrl=https%3A%2F%2Fsafe-app.morpho.org) to capture payload or grab `tx_data` from https://rewards.morpho.org/v1/users/0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e/distributions and call `0x4095F064B8d3c3548A3bebfd0Bbfd04750E30077.multicall([<tx_data>])`

### Step 2: Configure Watchlist

Adjust the `reward_wei` in `gen_merkl_airdrops_watchlist.json` to match the claimable amount from step 1.

### Step 3: Determine User Shares

Run `python tools/python/gen_merkl_airdrops.py` and upload the airdrop json artifact to https://merkl.angle.money/create/drop. Click `Preview Transaction` -> `Build a payload` -> `Download Safe Payload`.

### Step 4: Consolidate both Payloads

Add the `multicall` transaction from step 1 to the payload json artifact downloaded in step 3, as the first transaction.

### Rename Final Payload and Upload

Rename final payload to `morpho-epoch_<#>.json` and place in `MaxiOps/merkl/payloads/`.
