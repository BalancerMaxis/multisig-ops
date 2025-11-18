# BIP-XXX: Revoke External Delegations and Enable Treasury Self-Delegation

**Author**: @0xDanko (Director of the Balancer Foundation and Treasury Council member)

## TL;DR

This proposal seeks to streamline the Balancer DAO's meta-governance strategy. It calls for revoking all current governance token delegations for assets held by the DAO Treasury, which requires revoking the delegation permissions from the Safe module managed by KPK.

Upon revocation, this proposal grants the Balancer Treasury Council the mandate to manage and be responsible for re-delegating these assets to entities, individuals, or service providers they determine are best aligned with the strategic interests of the Balancer ecosystem.

## Motivation

The Balancer DAO Treasury holds a significant and strategic portfolio of governance tokens from partner protocols (e.g., AURA, AAVE, GNO, COW and others). The voting power associated with these assets — political assets often called "meta-governance" — is a critical tool for advancing Balancer's interests, such as securing favorable integrations and supporting aligned ecosystem partners.

Currently, the management of this voting power is concentrated and mandated to @kpk, a single entity. To maximize our strategic influence, the Treasury Council can actively manage these delegations, being directly accountable to Balancer governance and able to adapt during constant shifts in the DeFi (political) landscape.

The current delegation arrangement was established through BIP-452 (AAVE/stkAAVE), BIP-611/850 (ARB), and BIP-739 (GGU), delegating significant voting power to external addresses. While these arrangements served their purpose at the time, the DAO's maturation and the establishment of the Treasury Council create an opportunity to bring this strategic asset under more direct and responsive governance control.

By consolidating this authority under the Treasury Council, the DAO ensures that this power is wielded by a dedicated group with an in-depth understanding of Balancer's financial and strategic position. This move centralizes responsibility, improves accountability, and empowers the TC to execute a clear, long-term vision for Balancer's influence across the DeFi ecosystem.

Revoking permissions from the Zodiac's roles modifier module (KPK) on top of the Treasury Safe is a necessary step to unwind the existing delegation structure and provide the Treasury Council with a clean slate to execute its new mandate.

The Treasury Council will be required to maintain a public and easily accessible record of its current delegations.

## Technical Specification

This proposal authorizes the revocation of all external governance token delegations currently held by Balancer DAO-controlled safes and establishes self-delegation (delegation to the treasury itself) as the default state.

### Scope of Changes

**Tokens and Delegations to be Revoked:**

| Token | Current Delegate | Amount | Chain | Safe |
|-------|-----------------|---------|-------|------|
| AAVE | `0x8787FC2De4De95c53e5E3a4e5459247D9773ea52` | Treasury balance | Mainnet | Karpatkey Managed Treasury |
| stkAAVE | `0x8787FC2De4De95c53e5E3a4e5459247D9773ea52` | Treasury balance (~1,500) | Mainnet | Karpatkey Managed Treasury |
| ARB | `0x583E3EDc26E1B8620341bce90547197bfE2c1ddD` | Treasury balance | Arbitrum | Karpatkey Managed Treasury |
| GGU (Gyroscope) | 3 individual delegates | 60 total | Mainnet | DAO Multisig |

### Implementation

**Mainnet Treasury (Chain ID: 1)**
- Execute `delegate(treasuryAddress)` on AAVE token contract
- Execute `delegate(treasuryAddress)` on stkAAVE token contract
- Safe: `0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89`

**Arbitrum Treasury (Chain ID: 42161)**
- Execute `delegate(treasuryAddress)` on ARB token contract
- Safe: `0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89`

**Mainnet DAO Multisig - GGU (Chain ID: 1)**
- Execute `delegateVote(delegate, 0)` for each of the three current delegates
- Safe: `0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f`


### Payload Files

Transaction payloads for execution:
- `BIP-XXX-revoke-delegations-to-self-mainnet.json` (AAVE, stkAAVE)
- `BIP-XXX-revoke-delegations-to-self-arbitrum.json` (ARB)
- `BIP-XXX-revoke-delegations-to-self-ggu-mainnet.json` (GGU revocations)

### References

**Original Delegation BIPs:**
- **BIP-452**: AAVE and stkAAVE delegation (2023-W41) - `BIPs/2023/2023-W41/BIP-452.json`
- **BIP-611**: ARB delegation (2024-W22) - `BIPs/2024/2024-W22/BIP-611-ARB-Delegation.json`
- **BIP-739**: Gyroscope GGU delegation (2024-W50) - `BIPs/2024/2024-W50/[BIP-739]-Delegate-Gyroscope-GGU-to-DAO-Participants.json`
- **BIP-850**: ARB delegation renewal (2025-W35) - `BIPs/2025-W35/BIP-850_ARB_Delegation.json`

**Token Contracts:**
- **AAVE Token** (Mainnet): https://etherscan.io/address/0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9
- **stkAAVE Token** (Mainnet): https://etherscan.io/address/0x4da27a545c0c5B758a6BA100e3a049001de870f5
- **ARB Token** (Arbitrum): https://arbiscan.io/address/0x912CE59144191C1204E64559FE8253a0e49E6548
- **GGU Governance** (Mainnet): https://etherscan.io/address/0xA2321E23B3060e160195E138b62F8498546B0247

---
