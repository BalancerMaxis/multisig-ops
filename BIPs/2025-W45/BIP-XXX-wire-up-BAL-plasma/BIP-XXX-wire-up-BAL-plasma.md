# [BIP-XXX] Wire Up BAL Token on Plasma Chain

## PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/2504

## Summary

This proposal establishes LayerZero cross-chain communication for the BAL token between Ethereum mainnet and Plasma chain, enabling veBAL system integration and BAL emissions on Plasma following the successful completion of Month 3 checkpoint criteria as per [BIP-871](https://forum.balancer.fi/t/bip-874-urgent-proposal-deploy-balancer-v3-on-plasma/6834).

## Introduction

Plasma chain has successfully met the Month 3 checkpoint requirements for strategic deployment confirmation:
- Total Value Locked (TVL) exceeds $75M
- DAO revenue from fees surpasses $15k
- At least 5 pools with $10M or more in TVL

Having achieved these milestones, this proposal proceeds with the next phase: wiring up the BAL token to enable deeper tokenomics integration and unlock veBAL governance and BAL emissions on Plasma chain.

## Motivation

The successful performance of Plasma chain demonstrates strong product-market fit and sustainable operations. Integrating the veBAL system and BAL emissions on Plasma will:

1. **Unlock BAL Emissions**: Activate gauge voting and BAL rewards for Plasma liquidity providers
2. **Strengthen Ecosystem**: Deepen the integration between Plasma and the broader Balancer ecosystem
3. **Fulfill Strategic Roadmap**: Complete the planned progression from checkpoint validation to full tokenomics integration

This wire-up is the technical prerequisite for enabling cross-chain BAL transfers and gauge functionality on Plasma, aligning with the strategic deployment framework established during the chain's launch.

## Technical Specification

This proposal configures the LayerZero bridge for BAL token on Ethereum mainnet to communicate with Plasma chain (LayerZero chain ID: 383).

### Contract Actions

**Target Contract**: `0xe15bcb9e0ea69e6ab9fa080c4c4a5632896298c3` (BAL token on Ethereum)

**Transaction 1: Set Trusted Remote Address**
```
Function: setTrustedRemoteAddress(uint16 _remoteChainId, bytes _remoteAddress)
Parameters:
  - _remoteChainId: 383 (Plasma LayerZero chain ID)
  - _remoteAddress: 0x22625eEDd92c81a219A83e1dc48f88d54786B017 (BAL token on Plasma)
```

This establishes a trusted connection between the BAL token contracts on Ethereum and Plasma, allowing secure cross-chain transfers via LayerZero.

**Transaction 2: Set Minimum Destination Gas**
```
Function: setMinDstGas(uint16 _dstChainId, uint16 _packetType, uint256 _minGas)
Parameters:
  - _dstChainId: 383 (Plasma LayerZero chain ID)
  - _packetType: 0 (standard transfer packet type)
  - _minGas: 10000 (minimum gas units required on destination)
```

This sets the minimum gas requirement for LayerZero message execution on Plasma, ensuring reliable cross-chain message delivery.

### Execution

The proposal will be executed via the DAO multisig (`0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f`) on Ethereum mainnet after a successful governance vote.
