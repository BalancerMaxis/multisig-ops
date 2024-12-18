# LZRateProviderPokerV1 


This is a very short writeup that needs to be updated as we get a bit further.

This thing pokes layer zero rate providers on mainnet to update rates on child chains.

Each poke costs 0.01 ETH which comes from the contract.  For it to keep working it needs to have enough eth to poke everything on the list, and enough link.


https://etherscan.io/address/0xdDd5FF0E581f097573B13f247F6BE736f602F839#readContract

You can see which rate providers are poked by calling getRateProviders.

The owner can add and remove rate providers with the write functions that have sensible names.

The contract requires `(num rate providers)*0.01*(num days)` ETH to keep working.
