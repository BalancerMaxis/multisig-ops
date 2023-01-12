## Welcome to the Balancer Multisig Operations Repo
This repo is used to store payloads uploaded to the multisig, as well as any tooling used to generate such payloads.

### Uploading transaction JSONs as part of Balancer Governance
Balancer Governance requires that a link to a PR request in this repo with a gnosis-safe transaction builder JSON is included.

PR's should be to include a single file named `BIP-XXX.json` in the `BIPs` directory where XXX is the number of the BIP.  The PR should include the BIP title as it's commit/pr text. 
#### Examples
Here are some documents of how to do specific, commonly requested things.

| Link                                            | Description                                                   | Difficulty/Complexity                |
|-------------------------------------------------|---------------------------------------------------------------|--------------------------------------|
| [Add Gauge to veBAL](Examples/gauge-request)    | Add a gauge to veBAL and upload it                            | Low - Noob                           |
| [Transfer DAO Funds](Examples/funding)          | Transfer funds from the treasury one or more other addresses  | Low - Noob                           |
| [Gauge Replacement](Examples/gauge-replacement) | Kill one gauge and add another for pool or gauge replacements | Moderate - Requires basic git skillz |



### Balancer Multisigs
Here are a list of multisigs that the Maxis can and may load transactions into due to governance snapshots.

| Name                          | Purpose                                                                                                                                 | Chain                                                                                                                                                                                                                                                                           | Address                                     |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| Protocol Fees Multisig        | Collect fees, and set A-Factors and Fees on pools (default pool-owner, except on mainnet where a separate multisig is used to set fees. | [MAINNET](https://gnosis-safe.io/app/eth:0x7c68c42De679ffB0f16216154C996C354cF1161B/home), [ARBI](https://gnosis-safe.io/app/arb1:0x7c68c42De679ffB0f16216154C996C354cF1161B/home), [POLYGON](https://gnosis-safe.io/app/matic:0x7c68c42De679ffB0f16216154C996C354cF1161B/home) | 0x7c68c42De679ffB0f16216154C996C354cF1161B  |
| Mainnet Fee Setter            | Default pool owner for Mainnet that can set A-Factors and protocol fees.                                                                | [MAINNET](https://gnosis-safe.io/app/eth:0xf4A80929163C5179Ca042E1B292F5EFBBE3D89e6/home)                                                                                                                                                                                       | 0xf4A80929163C5179Ca042E1B292F5EFBBE3D89e6  |
| DAO Multlsig                  | DAO Treasury - funding BIPs go here                                                                                                     | [MAINNET](https://gnosis-safe.io/app/eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f/home)                                                                                                                                                                                       | 0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f  |
| Gauge Controller(LM Multisig) | Used to manage gauges and Reward Tokens and manage liquidity supplied to multichain (bridge).  New Gauge requests go here.              | [MAINNET](https://gnosis-safe.io/app/eth:0xc38c5f97B34E175FFd35407fc91a937300E33860/home), [ARBI](https://gnosis-safe.io/app/arb1:0xc38c5f97B34E175FFd35407fc91a937300E33860/home), [POLYGON](https://gnosis-safe.io/app/matic:0xc38c5f97B34E175FFd35407fc91a937300E33860/home) | 0xc38c5f97B34E175FFd35407fc91a937300E33860  |
| Linear Pool Control           | Manage limits on Mainnet Linear Pools                                                                                                   | [MAINNET](https://gnosis-safe.io/app/eth:0x75a52c0e32397A3FC0c052E2CeB3479802713Cf4/home)                                                                                                                                                                                       | 0x75a52c0e32397A3FC0c052E2CeB3479802713Cf4  |
| Maxi Operational Payments     | Holds the Maxi Budget and is used to pay people and expenses.                                                                           | [MAINNET](https://gnosis-safe.io/app/eth:0x166f54F44F271407f24AA1BE415a730035637325/home)                                                                                                                                                                                       | 0x166f54F44F271407f24AA1BE415a730035637325  |

### Optimism Multisigs
**PENDING: TODO**

### Ecosystem Multisigs
Here are a list of multisigs that have frequent interactions with BalancerDAO but are not managed in any way by the Maxis and are not triggered by snapshot votes.

| Name             | Purpose                                                                                               | Chain                                                                                     | Address                                    |
|------------------|-------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|--------------------------------------------|
| Balancer Grants  | Multisig funded by the Balancer treasury with funds managed by the community elected Grants Committee | [MAINNET](https://gnosis-safe.io/app/eth:0xE2c91f3409Ad6d8cE3a2E2eb330790398CB23597/home) | 0xE2c91f3409Ad6d8cE3a2E2eb330790398CB23597 | 

### Commonly used target addresses

| Name                | Address                                    | Purpose                               |
|---------------------|--------------------------------------------|---------------------------------------|
| GaugeAdder          | 0x2fFB7B215Ae7F088eC2530C7aa8E1B24E398f26a | Adding New Gauges                     |
| AuthorizerAdaptor   | 0x8F42aDBbA1B16EaAE3BB5754915E0D06059aDd75 | Accessing functions via granted roles |


### Need Help
You can contact Tritium, Solarcurve or any of the BAL Maxis on the Balancer Discord for help getting your JSON PR submitted.  We can also just do it for you if that's what you'd prefer.
