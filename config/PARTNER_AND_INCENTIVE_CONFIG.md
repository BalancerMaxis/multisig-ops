# Configuration Documentation

## Adding Partners

### Quick Steps

1. Add partner object to `partners` array in `config/partner_fee_share.json`:

```json
{
  "name": "PartnerName",
  "multisig_address": "0x...",
  "active": true,
  "fee_allocations": {
    "core_with_gauge": {
      "vebal_share_pct": 0.0625,
      "vote_incentive_pct": 0.7,
      "partner_share_pct": 0.15,
      "dao_share_pct": 0.0875
    },
    "non_core_with_gauge": {
      "vebal_share_pct": 0.25,
      "vote_incentive_pct": 0.0,
      "partner_share_pct": 0.5,
      "dao_share_pct": 0.25
    },
    "non_core_without_gauge": {
      "vebal_share_pct": 0.30,
      "vote_incentive_pct": 0.0,
      "partner_share_pct": 0.45,
      "dao_share_pct": 0.25
    }
  }
}
```

**Note:**
- Pools are discovered dynamically based on the partner name
- If `fee_allocations` are not specified, the partner will use the default allocations from `partner_fee_allocations`
- Each fee allocation must have three scenarios: `core_with_gauge`, `non_core_with_gauge`, and `non_core_without_gauge`
- All percentages in each scenario must sum to 1.0

## Adding Alliance Members

### Quick Steps

1. Add pools to existing alliance member's `pools` array in `config/alliance_fee_share.json`:

```json
{
  "pool_id": "0x...",
  "network": "mainnet",
  "partner": "Alliance Member Name",
  "eligibility_date": "YYYY-MM-DD",
  "active": true
}
```

**Note:** Alliance members use fee allocations from `alliance_fee_allocations.core` or `alliance_fee_allocations.non_core` based on whether the pool is core or non-core (determined dynamically).

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
      "eligibility_date": "YYYY-MM-DD",
      "active": true
    }
  ]
}
```

### Notes

- `partner` field in pools must match the alliance member's `name`
- Pool core/non-core status is determined dynamically

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