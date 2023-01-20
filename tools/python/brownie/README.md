# Balancer Maxi's Multisig Management Repo
#### Based of the [BadgerDAO Multisig Operations Repo](https://github.com/Badger-Finance/badger-multisig)

This repo is where all EVM multisig operations take place for the Badger DAO.
It relies heavily on [`ganache-cli`](https://docs.nethereum.com/en/latest/ethereum-and-clients/ganache-cli/), [`eth-brownie`](https://github.com/eth-brownie/brownie), [`gnosis-py`](https://github.com/gnosis/gnosis-py) and a custom developed evolution of [`ape-safe`](https://github.com/banteg/ape-safe); [`great-ape-safe`](https://github.com/gosuto-ai/great-ape-safe).

## Installation

The recommended version of Python for this repository is 3.9

```
python3.9 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

On an M1 Macbook you'll have to downgrade the regex package:
```
pip3 install regex==2021.09.30
```
Ignore the warnings about version conflict.

## Now what
The primary use of this repo right now is to post bribes. To do that:

- Look in REPO_ROOT/Bribs/LSDexample.csv
- Make a csv that follows this formant in the same folder (ensure no spaces before/after ,'s)
- Get brownie working and ganache-cli installed
- Run something like: `brownie run --network mainnet-fork scripts/maxi_operations/bribe_ecosystems.py main ../../../BRIBs/LSDexample.csv 0x12ceba0ede49feef56e9f3690869536944618da9a0da3a726e2db089440dacf1`
- - The big 0x string is the end part of the URL from the currently running aura snapshot

This will simulate everything on fork, pay out some bribes, and if everything adds up prompt you to 
specify an eth account to use to push the transaction to gnosis. Note that this account must be authorized
to post transactions to the BalancerDAO Fees Multisig on mainnet.
