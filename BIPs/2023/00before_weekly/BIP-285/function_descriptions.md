| function                      | description                                                                                                    |
|:------------------------------|:---------------------------------------------------------------------------------------------------------------|
| disable()                     | Disables new creation of pools from a pool factory.                                                            |
| enableRecoveryMode()          | Puts a pool into [Recovery Mode](https://medium.com/@0xSkly/inside-balancer-code-recoverymode-9af34ce5ab72)    |
| pause()                       | Stops trading in a pool.  Proportinal withdraws are still possible.                                            |
| setSwapFeePercentage(uint256) | **Pools:** Authorize change of swap fees for pools that delegate ownership to Balancer Governance: 0xba1ba1... |
|                               |  **Deployments**: Sets the protocol fee charged on swaps for this deployment                                   |