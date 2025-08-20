# Configuration Documentation

## Adding Partners

### Quick Steps

1. Add partner object to `partners` array in `config/alliance_fee_share.json`:

```json
{
  "name": "PartnerName",
  "multisig_address": "0x...",
  "active": true,
  "pools": [
    {
      "pool_id": "0x...",
      "network": "mainnet",
      "eligibility_date": "YYYY-MM-DD",
      "active": true
    }
  ]
}
```

**Note:** Partners will use the default allocation from `partner_fee_allocations.default` unless a custom allocation is specified. To override, add:

```json
{
  "name": "PartnerName",
  "multisig_address": "0x...",
  "active": true,
  "pools": [...],
  "custom_fee_allocation": {
    "vebal_share_pct": 0.125,
    "vote_incentive_pct": 0.35,
    "partner_share_pct": 0.35,
    "dao_share_pct": 0.175
  }
}
```

## Adding Alliance Members

### Quick Steps

1. Add pools to existing alliance member's `pools` array in `config/alliance_fee_share.json`:

```json
{
  "pool_id": "0x...",
  "network": "mainnet",
  "partner": "Alliance Member Name",
  "pool_type": "core",
  "eligibility_date": "YYYY-MM-DD",
  "active": true
}
```

**Note:** Alliance members use fee allocations from `alliance_fee_allocations.core` or `alliance_fee_allocations.non_core` based on `pool_type`.

### Adding New Alliance Member

```json
{
  "name": "New Alliance Member",
  "multisig_address": "0x...",
  "active": true,
  "join_date": "YYYY-MM-DD",
  "last_lock_date": "YYYY-MM-DD",
  "pools": [
    {
      "pool_id": "0x...",
      "network": "mainnet",
      "partner": "New Alliance Member",
      "pool_type": "core",
      "eligibility_date": "YYYY-MM-DD",
      "active": true
    }
  ]
}
```

### Notes

- `pool_type` must be either "core" or "non_core"
- `partner` field in pools must match the alliance member's `name`

## Pool Incentives Overrides

Configure voting and market overrides in `config/pool_incentives_overrides.json`:

```json
{
  "0xPoolId": {
    "voting_pool_override": "bal",
    "market_override": "hh"
  }
}
```

### Valid Options

- `voting_pool_override`: "bal" or "aura"
- `market_override`: "hh" or "paladin"

### Example

```json
{
  "0x5c6ee304399dbdb9c8ef030ab642b10820db8f56000200000000000000000014": {
    "voting_pool_override": "aura",
    "market_override": "paladin"
  }
}
```