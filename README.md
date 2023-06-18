## Welcome to the Balancer Multisig Operations Repo
This repo is used to store payloads uploaded to the multisig, as well as any tooling used to generate such payloads.

You can find a FAQ about snapshot handling here: [FAQ](FAQ.md)

## The Multisigs
Information about all of the Multisigs that the Maxis may load transactions into are in [multisigs.md](multisigs.md)

## Uploading transaction JSONs as part of Balancer Governance
Balancer Governance requires that a link to a PR request in this repo with a gnosis-safe transaction builder JSON is included.

PR's should be to include a single file named `BIP-XXX.json` in the `BIPs` directory where XXX is the number of the BIP.  The PR should include the BIP title as it's commit/pr text. 
### Examples
We are slowly developing a library of detailed examples for how to build BIP payloads based on common actions.
These examples can be found [HERE](BIPs/00examples)


### Chain Link keepers
The Maxi's have started using Chain Link automation to automate some regular processes that don't need deep review.  The first example of this is a automatic GasStation that keeps maxi deployer wallets topped up with ETH for depoloying pools and executing multisig transactions.  The table below describes all currently running upkeeps.  Links in the upkeep name column link to more detailed docs about the given upkeep.

| Upkeep Name                                          | Upkeep Contract                                                                    | Upkeep URL                                                                                                                  | Active? |
|------------------------------------------------------|------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|---------|
| [Maxi Gas Station](chainlink_keepers/maxiGasStation.md) | [MAINNET](https://etherscan.io/address/0x2F1901f2A82fcC3Ee9010b809938816B3b06FA6A) | [LINK](https://automation.chain.link/mainnet/62602467182204477380138952081172885895406053754821061796893606503759482417757) | Yes     |

Chainlinks documation around this automation setup can be found [here](https://docs.chain.link/chainlink-automation/introduction).
### Governance Process
Verbose and up-to-date docs about the balancer governance process can be found on [docs.balancer.fi](https://docs.balancer.fi/concepts/governance/)

### Need Help
You can contact Tritium, Solarcurve or any of the BAL Maxis on the Balancer Discord for help getting your JSON PR submitted.  We can also just do it for you if that's what you'd prefer.


