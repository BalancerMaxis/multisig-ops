## Welcome to the Balancer Multisig Operations Repo

This repo is used to store payloads uploaded to the multisig, as well as any tooling used to generate such payloads.

You can find a FAQ about snapshot handling here: [FAQ](FAQ.md)

## The Multisigs

Information about all of the Multisigs that the Maxis may load transactions into are in [multisigs.md](multisigs.md)

## Uploading transaction JSONs as part of Balancer Governance

Balancer Governance requires that a link to a PR request in this repo with a gnosis-safe transaction builder JSON is included.

- Set up a branch for your payload, but don't number the BIP yet. E.g. `bip-xxx-some_title`
- Place the payload in `BIP-XXX-some_title.json` in `BIPS/00proposed/`
- Open a PR with the title: "BIP-XXX: Some Title"
- Let the GitHub actions verify the payload file and generate a report of the payload

A post can now be created on the forum with the title "BIP-XXX: Some Title" linking to this PR.

Here is the minimal viable framework for a Balancer Governance acceptable payload

```json
{
  "version": "1.0",
  "chainId": "1",
  "createdAt": 1685637015445,
  "meta": {
    "name": "Transactions Batch",
    "description": "",
    "txBuilderVersion": "1.14.1",
    "createdFromSafeAddress": "0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f",
    "bipNumber": 42069
  },
  "transactions": []
}
```

All payloads MUST include the following in the global section:

- `createdFromSafeAddress`: That matches a known balancer multisig
- `chainId`: Must be the numeric chain ID of the chain to run on

Note that the `bipNumber` will be added later, once the forum proposal has been assigned a number.

You can provide more details in name and description if you want.

The transaction list takes the format of a standard gnosis tx builder list.

### Examples

We are slowly developing a library of detailed examples for how to build BIP payloads based on common actions.
These examples can be found [HERE](BIPs/00examples)

### Chainlink Upkeeps

The Maxi's have started using Chainlink automation to automate some regular processes that don't need deep review.

Documentation of our various running keepers can be found in [chainlink_keepers](./chainlink_keepers)
Chainlinks documation around this automation setup can be found [here](https://docs.chain.link/chainlink-automation/introduction).

### Governance Process

Verbose and up-to-date docs about the balancer governance process can be found on [docs.balancer.fi](https://docs.balancer.fi/concepts/governance/)

### Fees and Bribs

- Check out the [Bribs](./Bribs) for artifacts from our Core Pools Fee redirection processes (BIP-19)
- Check out [FeeSweep](./FeeSweep) for artifacts and info about our protocol fee processing activities

### Assorted Tooling

- [tools](./tools) is a somewhat messy directory with a bunch of reports/automations and scripts we use to deal with the various workloads.
- [action-scripts](./action-scripts) is where we build more final code and integrate more hashed out automations into github actions.

### Need Help

You can contact Tritium, Solarcurve or any of the BAL Maxis on the Balancer Discord for help getting your JSON PR submitted. We can also just do it for you if that's what you'd prefer.
