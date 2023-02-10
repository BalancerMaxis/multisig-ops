## Welcome to the Balancer Multisig Operations Repo
This repo is used to store payloads uploaded to the multisig, as well as any tooling used to generate such payloads.

You can find a FAQ about snapshot handling here: [FAQ](FAQ.md)

### Uploading transaction JSONs as part of Balancer Governance
Balancer Governance requires that a link to a PR request in this repo with a gnosis-safe transaction builder JSON is included.

PR's should be to include a single file named `BIP-XXX.json` in the `BIPs` directory where XXX is the number of the BIP.  The PR should include the BIP title as it's commit/pr text. 
#### Examples
Here are some documents of how to do specific, commonly requested things.

| Link                                                   | Description                                                   | Difficulty/Complexity                |
|--------------------------------------------------------|---------------------------------------------------------------|--------------------------------------|
| [Add Gauge to veBAL](BIPs/00examples/gauge-request)    | Add a gauge to veBAL and upload it                            | Low - Noob                           |
| [Transfer DAO Funds](BIPs/00examples/funding)          | Transfer funds from the treasury one or more other addresses  | Low - Noob                           |
| [Gauge Replacement](BIPS/00examples/gauge-replacement) | Kill one gauge and add another for pool or gauge replacements | Moderate - Requires basic git skillz |



### Balancer Multisigs
Here are a list of multisigs that the Maxis can and may load transactions into due to governance snapshots.

| Name                          | Purpose                                                                                                                                 | Chain                                                                                                                                                                                                                                                                           | Address                                     | Signer Set  |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|-------------|
| Protocol Fees Multisig        | Collect fees, and set A-Factors and Fees on pools (default pool-owner, except on mainnet where a separate multisig is used to set fees. | [MAINNET](https://gnosis-safe.io/app/eth:0x7c68c42De679ffB0f16216154C996C354cF1161B/home), [ARBI](https://gnosis-safe.io/app/arb1:0x7c68c42De679ffB0f16216154C996C354cF1161B/home), [POLYGON](https://gnosis-safe.io/app/matic:0x7c68c42De679ffB0f16216154C996C354cF1161B/home) | 0x7c68c42De679ffB0f16216154C996C354cF1161B  | Bal Maxis   |
| Mainnet Fee Setter            | Default pool owner for Mainnet that can set A-Factors and protocol fees.                                                                | [MAINNET](https://gnosis-safe.io/app/eth:0xf4A80929163C5179Ca042E1B292F5EFBBE3D89e6/home)                                                                                                                                                                                       | 0xf4A80929163C5179Ca042E1B292F5EFBBE3D89e6  | Bal Maxis   |
| DAO Multlsig                  | Funding BIPs, killing of gauges, veBAL whitelisting                                                                                     | [MAINNET](https://gnosis-safe.io/app/eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f/home)                                                                                                                                                                                       | 0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f  | DAO Signers |
| Gauge Controller(LM Multisig) | Used to manage gauges and Reward Tokens and manage liquidity supplied to multichain (bridge).  New Gauge requests go here.              | [MAINNET](https://gnosis-safe.io/app/eth:0xc38c5f97B34E175FFd35407fc91a937300E33860/home), [ARBI](https://gnosis-safe.io/app/arb1:0xc38c5f97B34E175FFd35407fc91a937300E33860/home), [POLYGON](https://gnosis-safe.io/app/matic:0xc38c5f97B34E175FFd35407fc91a937300E33860/home) | 0xc38c5f97B34E175FFd35407fc91a937300E33860  | Bal Maxis   |
| Linear Pool Control           | Manage limits on Mainnet Linear Pools                                                                                                   | [MAINNET](https://gnosis-safe.io/app/eth:0x75a52c0e32397A3FC0c052E2CeB3479802713Cf4/home)                                                                                                                                                                                       | 0x75a52c0e32397A3FC0c052E2CeB3479802713Cf4  | Bal Maxis   |
| Maxi Operational Payments     | Holds the Maxi Budget and is used to pay people and expenses.                                                                           | [MAINNET](https://gnosis-safe.io/app/eth:0x166f54F44F271407f24AA1BE415a730035637325/home)                                                                                                                                                                                       | 0x166f54F44F271407f24AA1BE415a730035637325  | Bal Maxis   |
| Managed Treasury              | Holds treasury funds managed by Karpatkey as per [BIP-162](https://forum.balancer.fi/t/bip-162-karpatkey-investment-strategy)           | [MAINNET](https://app.safe.global/eth:0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89/home)                                                                                                                                                                                          | 0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89  | DAO Signers |
| Arbitrum DAO Multisig         | Treasury + Admin functions on Arbitrum                                                                                                  | [ARBI](https://app.safe.global/arb1:0xaF23DC5983230E9eEAf93280e312e57539D098D0/home)                                                                                                                                                                                            | 0xaF23DC5983230E9eEAf93280e312e57539D098D0  | DAO Signers |
| Polygon DAO Multisig          | Treasury + Admin functions on Polygon                                                                                                   | [POLYGON](https://app.safe.global/matic:0xeE071f4B516F69a1603dA393CdE8e76C40E5Be85/home)                                                                                                                                                                                        | 0xeE071f4B516F69a1603dA393CdE8e76C40E5Be85  | DAO Signers |


### Optimism Multisigs
Optimism Multisigs are for the most part managed by the Beethoven team.

**PENDING: Add Information about Optimism Multisigs with BalancerDAO signers**



### Ecosystem Multisigs
Here are a list of multisigs that have frequent interactions with BalancerDAO but are not managed in any way by the Maxis and are not triggered by snapshot votes.

| Name             | Purpose                                                             Fetjer                            | Chain                                                                                     | Address                                    |
|------------------|-------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|--------------------------------------------|
| Balancer Grants  | Multisig funded by the Balancer treasury with funds managed by the community elected Grants Committee | [MAINNET](https://gnosis-safe.io/app/eth:0xE2c91f3409Ad6d8cE3a2E2eb330790398CB23597/home) | 0xE2c91f3409Ad6d8cE3a2E2eb330790398CB23597 | 

### Multisig Signer Sets

#### DAO Multisigs Signer set
| Signer                                             | Association              | Address                                     |
|----------------------------------------------------|--------------------------|---------------------------------------------|
| [Alexander Lange](https://twitter.com/AlexLangeVC) | \(Inflection\)           | 0x3ABDc84Dd15b0058B281D7e26CCc3932cfb268aA  |
| [0xMaki](https://twitter.com/0xMaki)               | \(LayerZero, AURA, DCV\) | 0x285b7EEa81a5B66B62e7276a24c1e0F83F7409c1  |
| [Solarcurve](https://twitter.com/0xSolarcurve)     | \(Balancer Maxis\)       | 0x512fce9B07Ce64590849115EE6B32fd40eC0f5F3  |
| [Evan](https://twitter.com/0xSausageDoge)          | \(Fjord\)                | 0x59693BA1A5764e087CE166ac0E0085Fc071B9ea7  |
| [Ernesto](https://twitter.com/eboadom)             | \(BGD\)                  | 0xA39a62304d8d43B35114ad7bd1258B0E50e139b3  |
| [Mounir](https://twitter.com/mounibec)             | \(Paraswap\)             | 0x0951FF0835302929d6c0162b3d2495A85e38ec3A  |
| [Trent McConaghy](https://twitter.com/trentmc0)    | \(Ocean Protocol\)       | 0x478eC43c6867c2884f87B21c164f1fD1308bD9a3  |
| [Stefan](https://twitter.com/StefanDGeorge)        | \(Gnosis\)               | 0x9F7dfAb2222A473284205cdDF08a677726d786A0  |
| [bonustrack87](https://twitter.com/bonustrack87)   | \(Snapshot\)             | 0x9BE6ff2A1D5139Eda96339E2644dC1F05d803600  |
 | [nanexcool](https://twitter.com/nanexcool)         | \(Ethereum OG\)          | 0x823DF0278e4998cD0D06FB857fBD51e85b18A250  |
 | [David Gerai](https://twitter.com/davgarai)        | \(Nostra Finance\)       | 0xAc1aA53108712d7f38093A67d380aD54B562a650  |

**DAO Multisigs always require 6/11 signers to execute a transaction.**


Beyond those current signers, [BIP-16](https://forum.balancer.fi/t/bip-16-update-dao-multisig-replacement-list/3361) laid
out a group of backup signers who could replace current signers without further governance.  Note that since BIP-16,
Moniur has become an active member of the DAO multisig.

#### Operational Multisigs Signer Set (Balancer Maxis)
| Signer       | Discord Handle  | Address                                     |
|--------------|-----------------|---------------------------------------------|
| Solarcurve   | solarcurve#5075 | 0x512fce9B07Ce64590849115EE6B32fd40eC0f5F3  |
| Zen Dragon   | Zen Dragon#2923 | 0x7c2eA10D3e5922ba3bBBafa39Dc0677353D2AF17  |
| Zekraken     | zekraken#0645   | 0xafFC70b81D54F229A5F50ec07e2c76D2AAAD07Ae  |
| Mike B       | d_w_b_w_d#0685  | 0xc4591c41e01a7a654B5427f39Bbd1dEe5bD45D1D  |
| Xeonus       | Xeonus#4620     | 0x7019Be4E4eB74cA5F61224FeAf687d2b43998516  |
| Danko        | 0xDanko#3565    | 0x200550cAD164E8e0Cb544A9c7Dc5c833122C1438  |
| Tritium      | Trtiium#0069    | 0xcf4fF1e03830D692F52EB094c52A5A6A2181Ab3F  |

**The Balancer Maxi Multisig set requires 2 or 3 out of 7 signers to execute, depending on the security level of the Multisig.**

The Balancer Maxi's are ratified by a BIP each quarter.  [BIP-145](https://forum.balancer.fi/t/bip-145-fund-the-balancer-maxis-for-q1-2023/)
is a recent example of such governance.

### Commonly used target addresses

| Name                | Address                                    | Purpose                               |
|---------------------|--------------------------------------------|---------------------------------------|
| GaugeAdder          | 0x2fFB7B215Ae7F088eC2530C7aa8E1B24E398f26a | Adding New Gauges                     |
| AuthorizerAdaptor   | 0x8F42aDBbA1B16EaAE3BB5754915E0D06059aDd75 | Accessing functions via granted roles |


### Need Help
You can contact Tritium, Solarcurve or any of the BAL Maxis on the Balancer Discord for help getting your JSON PR submitted.  We can also just do it for you if that's what you'd prefer.
