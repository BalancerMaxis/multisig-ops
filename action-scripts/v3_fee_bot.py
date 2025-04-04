import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pprint import pprint

from bal_addresses import AddrBook, to_checksum_address
from bal_tools import Subgraph
from web3 import Web3
from web3.exceptions import ContractLogicError


CONFIG = json.load(open("action-scripts/v3_fee_config.json"))


def get_prices(chain: str):
    return dict(
        [
            (token["address"], Decimal(token["price"]))
            for token in s.fetch_graphql_data(
                "apiv3", "get_prices", {"chains": [chain.upper()]}
            )["tokenGetCurrentPrices"]
        ]
    )


def get_pools(chain: str, broadcast: bool = False):
    drpc = Web3(
        Web3.HTTPProvider(
            f"https://lb.drpc.org/ogrpc?network={('ethereum' if chain == 'mainnet' else chain)}&dkey={os.getenv('DRPC_KEY')}"
        )
    )
    bot = drpc.eth.account.from_key(os.getenv("PRIVATE_KEY"))
    sweeper = AddrBook(chain).search_unique("20250228-v3-protocol-fee-sweeper").address
    burner = AddrBook(chain).search_unique("20250221-v3-cow-swap-fee-burner").address
    threshold = Decimal(CONFIG[chain]["usdc_threshold"])
    max_gas_price = int(CONFIG[chain]["max_gas_price"])
    max_priority_fee = int(CONFIG[chain]["max_priority_fee"])
    for pool in s.fetch_graphql_data("apiv3", "get_pools", {"chain": chain.upper()})[
        "poolGetPools"
    ]:
        if pool["protocolVersion"] != 3:
            continue
        report[chain]["n_pools"] += 1
        print(
            f"checking for pending fees on {chain}:{pool['address']} ({pool['symbol']})..."
        )
        fees = s.fetch_graphql_data(
            "vault-v3", "get_v3_fees", {"poolId": pool["address"].lower()}
        )
        if fees["pool"]:
            for token in fees["pool"]["tokens"]:
                fees_vault = Decimal(token["vaultProtocolSwapFeeBalance"]) + Decimal(
                    token["vaultProtocolYieldFeeBalance"]
                )
                fees_controller = Decimal(token["controllerProtocolFeeBalance"])
                if fees_vault > 0 or fees_controller > 0:
                    try:
                        potential = (fees_vault + fees_controller) * prices[
                            token["address"]
                        ]
                        if potential <= 0:
                            print("!!! incorrect price for", token["address"])
                            continue
                    except KeyError:
                        print("!!! no price for", token["address"])
                        continue
                    report[chain]["total_potential"] += potential
                    print("token:", token["symbol"], token["address"])
                    print("price:", f"${prices[token['address']]}")
                    print("collectable in vault:", fees_vault, token["symbol"])
                    print("sweepable in controller:", fees_controller, token["symbol"])
                    if potential < threshold:
                        print(f"not enough fees to burn; only worth {potential} USDC\n")
                        continue
                    print("burning for:", potential, "USDC"),

                    deadline = int(
                        datetime.timestamp(
                            datetime.now(timezone.utc) + timedelta(minutes=90)
                        )
                    )
                    ProtocolFeeSweeper = drpc.eth.contract(
                        address=sweeper,
                        abi=json.load(
                            open("action-scripts/abis/ProtocolFeeSweeper.json")
                        ),
                    )
                    if not ProtocolFeeSweeper.functions.isApprovedProtocolFeeBurner(
                        burner
                    ).call():
                        print("!!! burner not approved (yet); skipping\n")
                        continue
                    fee_data = drpc.eth.fee_history(1, "latest")
                    if fee_data.baseFeePerGas[-1] > max_gas_price:
                        print(
                            f"!!! base fee too high ({fee_data.baseFeePerGas[-1]}); skipping\n"
                        )
                        continue
                    try:
                        try:
                            max_priority_fee_latest = fee_data.reward[0][0]
                            if max_priority_fee_latest > 0:
                                max_priority_fee_optimal = min(
                                    max_priority_fee, max_priority_fee_latest
                                )
                        except:
                            max_priority_fee_optimal = max_priority_fee
                        unsigned_tx = (
                            ProtocolFeeSweeper.functions.sweepProtocolFeesForToken(
                                to_checksum_address(pool["address"]),
                                to_checksum_address(token["address"]),
                                int(threshold * Decimal("1e6")),
                                deadline,
                                burner,
                            ).build_transaction(
                                {
                                    "from": bot.address,
                                    "nonce": drpc.eth.get_transaction_count(
                                        bot.address
                                    ),
                                    "maxFeePerGas": max_gas_price,
                                    "maxPriorityFeePerGas": max_priority_fee_optimal,
                                }
                            )
                        )
                        print("tx: ", end="")
                        pprint(unsigned_tx)
                        signed_tx = drpc.eth.account.sign_transaction(
                            unsigned_tx, bot.key
                        )
                        if broadcast:
                            try:
                                tx_hash = drpc.eth.send_raw_transaction(
                                    signed_tx.raw_transaction
                                )
                                drpc.eth.wait_for_transaction_receipt(tx_hash)
                            except Exception as e:
                                print(f"!!! tx failed: {e}\n")
                                continue
                        print(
                            "tx hash:",
                            f"0x{tx_hash.hex()}\n" if broadcast else "<dry run>\n",
                        )
                    except ContractLogicError as e:
                        if e.data.startswith("0xd0c1b3cf"):
                            # OrderHasUnexpectedStatus
                            print("!!! token stuck in burner; no new order possible\n")


if __name__ == "__main__":
    report = {}
    for chain in CONFIG:
        report[chain] = {"n_pools": 0, "total_potential": 0}
        s = Subgraph(chain)
        prices = get_prices(chain)
        get_pools(chain)
    pprint(report)
    print(
        "total total_potential:",
        sum([chain["total_potential"] for chain in report.values()]),
    )
