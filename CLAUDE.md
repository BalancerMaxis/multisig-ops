# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the Balancer Multisig Operations repository used for managing and executing Balancer DAO governance proposals and operational transactions through Gnosis Safe multisigs. The repository primarily consists of JSON payloads for multisig transactions and Python scripts for automation.

## Development Setup

### Environment Setup
```bash
# Main project setup (using Pipfile)
pip install pipenv
pipenv install

# For brownie-specific tools (use Python 3.9)
cd tools/python/brownie
python3.9 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Create .env from template
cp .env.example .env
# Add INFURA_ID (required) and ETHERSCAN_TOKEN (recommended)
```

### Key Commands

**Linting:**
```bash
black .  # Python code formatting (auto-runs on PRs)
```

**BIP Validation:**
```bash
# From action-scripts/brownie/scripts/
python validate_bip.py [path_to_json]

# Or using brownie
brownie run scripts/validate_bip.py
```

**Common Operations:**
```bash
# Generate fee sweep payloads
python tools/python/sweepFees.py

# Generate merkle airdrops
python tools/python/gen_merkl_airdrops.py

# Process bribes
cd tools/python/brownie
brownie run --network mainnet-fork scripts/maxi_operations/bribe_ecosystems.py main ../../../BRIBs/example.csv [snapshot_id]

# Merge JSON payloads
python action-scripts/merge_pr_jsons.py
```

## Architecture

### Directory Structure
- **BIPs/**: Balancer Improvement Proposal payloads organized by week
  - `00proposed/`: New proposals awaiting approval
  - `00batched/`: Weekly batched payloads
  - `00examples/`: Template examples for common operations
- **MaxiOps/**: Operational transactions (fee management, rewards, etc.)
- **action-scripts/**: Production Python scripts for payload generation
- **tools/python/**: Development tools and utilities
- **config/**: Protocol configuration (core pools, fees, incentives)

### Key Patterns
1. **JSON Payloads**: All multisig transactions use Gnosis Safe Transaction Builder format
2. **Chain Support**: Scripts typically support all Balancer deployment chains (mainnet, arbitrum, polygon, etc.)
3. **Validation**: GitHub Actions automatically validate and report on all BIP submissions
4. **Multisig Structure**: Different safes for different functions (DAO Multisig, Fee Collector, LM Multisig)

### Workflow for BIPs
1. Create branch: `git checkout -b bip-xxx-descriptive_title`
2. Place payload in `BIPs/00proposed/BIP-XXX-descriptive_title.json`
3. Open PR titled "BIP-XXX: Descriptive Title"
4. GitHub Actions will validate and generate reports
5. After snapshot vote, payload moves to appropriate week folder

### Testing Approach
- Use `brownie run --network mainnet-fork` for testing transactions
- Validation scripts check payload structure and permissions
- Reports generated show transaction effects before execution

### Important Configuration
- **Multisig Addresses**: Found in `multisigs.md` and throughout config files
- **Chain IDs**: Must use numeric chain IDs in payloads (1 for mainnet, 42161 for arbitrum, etc.)
- **Dependencies**: `bal-addresses` package provides Balancer protocol addresses
- **Brownie Config**: Default network is mainnet-fork for testing

### Security Considerations
- All payloads require multisig execution (typically 6/11 for DAO, 2-3/7 for operational)
- Automated validation prevents common errors
- Emergency SubDAO handles time-sensitive operations
- Never commit private keys or sensitive data