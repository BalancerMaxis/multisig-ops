import datetime

from helpers.addresses import registry, r
from great_ape_safe import GreatApeSafe
import datetime

LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

### This script bridges coins from polygon to mainnet as part of BIP-162
### https://snapshot.org/#/balancer.eth/proposal/0xeb91b3428ad81bdcb840d83dc8977ae4ff5432d10ae338a8b890e7966248b7b2
### The script uses the across bridge which does not support WMATIC, so it will be manually bridged using multichain and a UI.

# BRIDGE the below tokens from polygon to mainnet
# tokens to bridge out
safe = GreatApeSafe(registry.poly.balancer.multisigs.lm)

# From BIP: From there, BPT will be withdrawn and all funds bridged back to Ethereum. USDC & WETH will be sent to the
# Karpatkey Safe 0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89,
# BAL & WMATIC sent to the Treasury 0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f
tokens_dest_map = {
        r.tokens.USDC: registry.eth.balancer.multisigs.karpatkey,
    #    registry.poly.tokens.WMATIC, #TODO bridge manually, across has no WMATIC support -> DAO MULTISIG
        r.tokens.WETH: registry.eth.balancer.multisigs.karpatkey,
        r.tokens.BAL: registry.eth.balancer.multisigs.dao
}

safe.take_snapshot(tokens_dest_map.keys())

destination_chain_id = 1

def main():

    safe.init_across()

    for token_address, recipient in tokens_dest_map.items():
        token = safe.contract(token_address)
        token_balance = token.balanceOf(safe.address)
        ##TODO remove test
        amount = int(token_balance) # TODO remove divisor for full amount
        if amount > 0:

            deadline = safe.across.bridge_token(recipient_address=recipient,
                                                origin_token=token,
                                                amount=amount,
                                                dest_chain_id=destination_chain_id
                                               )
            print(f">>>Bridging {amount/10**token.decimals()} of {token.symbol()} to {recipient} on chain with id {destination_chain_id} over Across.")
            print(f">>>Execute by {datetime.datetime.fromtimestamp(deadline).strftime('%Y-%m-%d %H:%M:%S')} {LOCAL_TIMEZONE}\n\n")
        else:
            print(f" === Balance for {token.symbol()} is zero === \n")

    safe.post_safe_tx(gen_tenderly=False)
