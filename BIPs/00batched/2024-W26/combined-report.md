
## Mainnet DAO Multisig
[Tenderly](https://dashboard.tenderly.co/public/safe/safe-apps/simulator/a074f965-8fc8-4cb8-b480-b27f40af8015)

[Sign Nonce 247](https://app.safe.global/transactions/queue?safe=eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)

---
FILENAME: `BIPs/00batched/2024-W26/1-0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f.json`
MULTISIG: `multisigs/dao (mainnet:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)`
COMMIT: `6f51e78984818972c7b3062d4dd76c47bd1d1217`
CHAIN(S): `mainnet`
TENDERLY: [SUCCESS](https://www.tdly.co/shared/simulation/222205a7-6af5-4981-90f3-e4ef60f5445b)
```
+--------------------------+--------------------------------------------------------------------+----------+-----+--------------------------------------------+------+------+---------+---------+----------+---------------------------------------------------------------------------------------------------------+
| function                 | pool_id                                                            | symbol   | a   | gauge_address                              | fee  | cap  | style   |   bip   | tx_index | tokens                                                                                                  |
+--------------------------+--------------------------------------------------------------------+----------+-----+--------------------------------------------+------+------+---------+---------+----------+---------------------------------------------------------------------------------------------------------+
| AAEntrypoint/killGauge() | 0xa7ff759dbef9f3efdd1d59beee44b966acafe214000200000000000000000180 | USDC-PAL | N/A | 0xe2b680A8d02fbf48C7D9465398C4225d7b7A7f87 | 1.0% | 2.0% | mainnet | BIP-636 |    7     | ['0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48: USDC', '0xAB846Fb6C81370327e784Ae7CbB6d6a6af6Ff4BF: PAL'] |
+--------------------------+--------------------------------------------------------------------+----------+-----+--------------------------------------------+------+------+---------+---------+----------+---------------------------------------------------------------------------------------------------------+
```
FILENAME: `BIPs/00batched/2024-W26/1-0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f.json`
MULTISIG: `multisigs/dao (mainnet:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f)`
COMMIT: `6f51e78984818972c7b3062d4dd76c47bd1d1217`
CHAIN(S): `mainnet`
TENDERLY: [SUCCESS](https://www.tdly.co/shared/simulation/4ad3f7fb-217e-4466-8d7a-91c5e96a8773)
```
+----------+-------------------------------------------------+-----------------------------------------------------------------------------+----------------------------------------+---------+----------+
| function | token_symbol                                    | recipient                                                                   | amount                                 |   bip   | tx_index |
+----------+-------------------------------------------------+-----------------------------------------------------------------------------+----------------------------------------+---------+----------+
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/beets_service_provider:0x811912c19eEF91b9Dc3cA52fc426590cFB84FC86 | 87000.0 (RAW: 87000000000)             | BIP-631 |    0     |
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/foundation_opco:0x3B8910F378034FD6E103Df958863e5c684072693        | 522168.0 (RAW: 522168000000)           | BIP-634 |    1     |
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/bizdev:0xC7E84373FC63A17B5B22EBaF86219141B630cD7a                 | 36000.0 (RAW: 36000000000)             | BIP-635 |    2     |
| transfer | BAL:0xba100000625a3754423978a60c9317c58a424e3D  | multisigs/bizdev:0xC7E84373FC63A17B5B22EBaF86219141B630cD7a                 | 4386.0 (RAW: 4386000000000000000000)   | BIP-635 |    3     |
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/grants_treasury:0xE2c91f3409Ad6d8cE3a2E2eb330790398CB23597        | 6900.0 (RAW: 6900000000)               | BIP-633 |    4     |
| transfer | BAL:0xba100000625a3754423978a60c9317c58a424e3D  | multisigs/grants_treasury:0xE2c91f3409Ad6d8cE3a2E2eb330790398CB23597        | 33527.0 (RAW: 33527000000000000000000) | BIP-633 |    5     |
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/beets_service_provider:0x811912c19eEF91b9Dc3cA52fc426590cFB84FC86 | 90000.0 (RAW: 90000000000)             | BIP-632 |    6     |
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/maxi_ops:0x166f54F44F271407f24AA1BE415a730035637325               | 172500.0 (RAW: 172500000000)           | BIP-630 |    8     |
| transfer | BAL:0xba100000625a3754423978a60c9317c58a424e3D  | multisigs/maxi_ops:0x166f54F44F271407f24AA1BE415a730035637325               | 14464.0 (RAW: 14464000000000000000000) | BIP-630 |    9     |
| transfer | USDC:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | multisigs/wonderland:0x74fEa3FB0eD030e9228026E7F413D66186d3D107             | 30000.0 (RAW: 30000000000)             | BIP-578 |    10    |
+----------+-------------------------------------------------+-----------------------------------------------------------------------------+----------------------------------------+---------+----------+
```
