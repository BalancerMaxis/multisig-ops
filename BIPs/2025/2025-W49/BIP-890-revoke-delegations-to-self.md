# BIP-XXX: Revoke External Delegations and Enable Treasury Self-Delegation

**Author**: @0xDanko (Director of the Balancer Foundation and Treasury Council member)

## TL;DR

This proposal seeks to streamline the Balancer DAO's meta-governance strategy. It calls for revoking all current governance token delegations for assets held by the DAO Treasury, which requires revoking the delegation permissions from the Safe module managed by KPK (to be posted on a future PUR by @kpk).

Upon approval, this proposal grants the Balancer Treasury Council the mandate to manage and be responsible for re-delegating these assets to entities, individuals, or service providers they determine are best aligned with the strategic interests of the Balancer ecosystem.

## Motivation

The Balancer DAO Treasury holds a significant and strategic portfolio of governance tokens from partner protocols (e.g., AURA, AAVE, GNO, COW and others). The voting power associated with these assets — political assets often called "meta-governance" — is a critical tool for advancing Balancer's interests, such as securing favorable integrations and supporting aligned ecosystem partners.

Currently, the management of this voting power is concentrated and mandated to KPK, a single entity (with some exceptions—see below). To maximize our strategic influence, the Treasury Council can actively manage these delegations, being directly accountable to Balancer governance and able to adapt during constant shifts in the DeFi (political) landscape.

By consolidating this authority under the Treasury Council, the DAO ensures that this power is wielded by a dedicated group with an in-depth understanding of Balancer's financial and strategic position. This move channels responsibility, improves accountability, and empowers the TC to execute a clear, long-term vision for Balancer's influence across the DeFi ecosystem.

Revoking permissions from the Zodiac's roles modifier module (KPK) on top of the Treasury Safe is a necessary step to unwind the existing delegation structure and provide the Treasury Council with a clean slate to execute its new mandate. It has been agreed by KPK to post on a future BIP (PUR #8) if this one is approved.

The Treasury Council will be required to maintain a public and easily accessible record of its current delegations.

### Current delegations

* AAVE / stkAAVE: delegated to @kpk (BIP-452, BIP-708)
* ARB: delegated to @kpk (BIP-611, BIP-850)
* GGU: delegated to @Xeonus @ZenDragon and @naly (BIP-739)
* MATIC: delegated to @0xDanko (BIP-851)
* GNO: no active delegation
* COW: no active delegation
* vlAURA: used to vote for gauge emissions, but no delegate set, currently managed by the MAXYZ operator safe

## Technical Specification

> This proposal authorizes the revocation of all external governance token delegations currently held by Balancer DAO-controlled safes and establishes self-delegation (delegation to the treasury itself) as the default state.

At the present time, the Treasury Council proposes only for the AAVE holdings to be re-delegated, considering other delegations (MATIC, GGU and ARB) to be appropriate.

### Scope of Changes

**Tokens and Delegations to be Revoked:**

| Token | Current Delegate | Amount | Chain | Safe |
|-------|-----------------|---------|-------|------|
| AAVE | `0x8787FC2De4De95c53e5E3a4e5459247D9773ea52` | Treasury balance | Mainnet | Karpatkey Managed Treasury |
| stkAAVE | `0x8787FC2De4De95c53e5E3a4e5459247D9773ea52` | Treasury balance (~1,500) | Mainnet | Karpatkey Managed Treasury |

### Implementation

**Mainnet Treasury (Chain ID: 1)**
- Execute `delegate(treasuryAddress)` on AAVE token contract
- Execute `delegate(treasuryAddress)` on stkAAVE token contract
- Safe: `0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89`

### Payload Files

Transaction payloads for execution:
- `BIP-XXX-revoke-delegations-to-self-mainnet.json` (AAVE, stkAAVE)

### References

**Original Delegation BIPs:**
- **BIP-452**: AAVE and stkAAVE delegation (2023-W41) - `BIPs/2023/2023-W41/BIP-452.json`

**Token Contracts:**
- **AAVE Token** (Mainnet): https://etherscan.io/address/0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9
- **stkAAVE Token** (Mainnet): https://etherscan.io/address/0x4da27a545c0c5B758a6BA100e3a049001de870f5

---
