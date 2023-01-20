# Balancer Maxi's GreatApe setup for multisig management
#### Based of the [BadgerDAO Multisig Operations Repo](https://github.com/Badger-Finance/badger-multisig)

It relies heavily on [`ganache-cli`](https://docs.nethereum.com/en/latest/ethereum-and-clients/ganache-cli/), [`eth-brownie`](https://github.com/eth-brownie/brownie), [`gnosis-py`](https://github.com/gnosis/gnosis-py) and a custom developed evolution of [`ape-safe`](https://github.com/banteg/ape-safe); [`great-ape-safe`](https://github.com/gosuto-ai/great-ape-safe).

## Installation

The recommended version of Python for this toolset is 3.9

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


## How to load transactions
The [Gnosis-Safe Delegator](https://gnosis-delegator.badger.com/) created by bounty funded by Badger can be used to
set delegates via a web browser and metamask to enable easy interaction with a hardware signer.

Delegation works like so:

- Any signer on a safe can set delegate addresses.
- Delegate addresses can load transactions to the safe, but can not sign (Transactions loaded with 0/x)
- If a signer is removed, their delegates go with them.

So a password protected or otherwise secured key can be setup in brownie for any operator who needs to load 
transactions.  This address can be added via the delegator.  The operator will then be able to load transactions without
having to deal with connecting a hardware signer to brownie.

It also allows different people to build transactions than those who sing them.

You can find source code from [Soptq](https://github.com/Soptq) the original author here [Gnosis-Safe Delegator on github](https://github.com/Soptq/gnosis-safe-delegate-dapp)