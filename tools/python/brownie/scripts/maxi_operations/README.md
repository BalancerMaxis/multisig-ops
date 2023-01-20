### Maxi Operations scripts

The below scripts are used for executing on governance topics and/or regular protocol operations.

For more instructions on how to get bronwie setup [check here](../../README.md)


| script              | description                             | Run example (from brownie root dir)                                                                                 |
|---------------------|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| bribe_ecosystem.py  | Used to post core pool bribs from a csv | `brownie run --network mainnet-fork scripts/maxi_operations/bribe_ecosystems.py main ../../../Bribs/LSDexample.csv` |  
 | disable_gauges.py   | Used to quickly kill a list of gauges   | `brownie run --network mainnet-fork scripts/maxi_operations/disable_gauges.py`                                      |