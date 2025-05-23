import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pprint import pprint
from time import sleep

from bal_addresses import AddrBook, to_checksum_address
from bal_addresses.addresses import ZERO_ADDRESS
from bal_tools import Subgraph
from web3 import Web3
from web3.exceptions import ContractLogicError


CONFIG = json.load(open("action-scripts/v3_fee_config.json"))
ORDER_COOLDOWN = 60 * 5  # 5 minutes
SLIPPAGE = Decimal("0.005")  # 50bips slippage
NULL = None
OMNI_MSIG = "0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e"


def get_prices(chain: str):
    return dict(
        [
            (token["address"], Decimal(token["price"]))
            for token in s.fetch_graphql_data(
                "apiv3", "get_prices", {"chains": [chain.upper()]}
            )["tokenGetCurrentPrices"]
        ]
    )


def _payload_template(chain_id, safe_address):
    return {
        "chainId": chain_id,
        "meta": {
            "name": "Transactions Batch",
            "createdFromSafeAddress": safe_address,
        },
        "transactions": [],
    }


def _tx_cancelOrder(burner_address, token_address):
    return {
        "to": burner_address,
        "value": "0",
        "data": NULL,
        "contractMethod": {
            "inputs": [
                {
                    "internalType": "contract IERC20",
                    "name": "tokenIn",
                    "type": "address",
                },
                {"internalType": "address", "name": "receiver", "type": "address"},
            ],
            "name": "cancelOrder",
            "payable": False,
        },
        "contractInputsValues": {
            "tokenIn": token_address,
            "receiver": OMNI_MSIG,
        },
    }


def _add_to_payload(
    DesignatedBurner, payload_unstuck_tokens, asset_address, designated_burner
):
    if DesignatedBurner.functions.getOrderStatus(
        to_checksum_address(asset_address)
    ).call() not in [0, 2]:
        # OrderStatus is neither NonExistent nor Filled, thus can be cancelled
        print("!!! token stuck in burner; adding to unstuck payload\n")
        for tx in payload_unstuck_tokens["transactions"]:
            if tx["contractInputsValues"]["tokenIn"].lower() == asset_address.lower():
                break
        else:
            print(f"adding {asset_address} to unstuck payload")
            payload_unstuck_tokens["transactions"].append(
                _tx_cancelOrder(
                    designated_burner,
                    to_checksum_address(asset_address),
                )
            )
    else:
        print("!!! token can neither be burned nor cancelled\n")


def get_pools(chain: str, broadcast: bool = False):
    drpc = Web3(
        Web3.HTTPProvider(
            f"https://lb.drpc.org/ogrpc?network={('ethereum' if chain == 'mainnet' else chain)}&dkey={os.getenv('DRPC_KEY')}"
        )
    )
    Bot = drpc.eth.account.from_key(os.getenv("PRIVATE_KEY"))
    sweeper = AddrBook(chain).search_unique("20250228-v3-protocol-fee-sweeper").address
    ProtocolFeeSweeper = drpc.eth.contract(
        address=sweeper,
        abi=json.load(open("action-scripts/abis/ProtocolFeeSweeper.json")),
    )
    target_token = ProtocolFeeSweeper.functions.getTargetToken().call().lower()
    burner = AddrBook(chain).search_unique("20250221-v3-cow-swap-fee-burner").address
    erc4626_burner = (
        AddrBook(chain).search_unique("20250507-v3-erc4626-cow-swap-fee-burner").address
    )
    payload_unstuck_tokens = _payload_template(str(drpc.eth.chain_id), OMNI_MSIG)
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
                for pool_token in pool["poolTokens"]:
                    if pool_token["address"].lower() == token["address"].lower():
                        token_is_erc4626 = pool_token["isErc4626"]
                        break
                if token_is_erc4626:
                    ERC4626 = drpc.eth.contract(
                        address=to_checksum_address(token["address"]),
                        abi=json.load(open("action-scripts/abis/ERC4626.json")),
                    )
                    asset_address = ERC4626.functions.asset().call()
                else:
                    asset_address = token["address"]
                Asset = drpc.eth.contract(
                    address=to_checksum_address(asset_address),
                    abi=json.load(open("action-scripts/abis/ERC20.json")),
                )
                designated_burner = erc4626_burner if token_is_erc4626 else burner
                DesignatedBurner = drpc.eth.contract(
                    address=to_checksum_address(designated_burner),
                    abi=json.load(
                        open("action-scripts/abis/IERC4626CowSwapFeeBurner.json")
                    ),
                )
                balance = Asset.functions.balanceOf(designated_burner).call()
                if balance > 0:
                    if DesignatedBurner.functions.getOrderStatus(
                        to_checksum_address(asset_address)
                    ).call() not in [0, 2]:
                        # OrderStatus is neither NonExistent nor Filled, thus can be cancelled
                        _add_to_payload(
                            DesignatedBurner,
                            payload_unstuck_tokens,
                            asset_address,
                            designated_burner,
                        )
                fees_vault = Decimal(token["vaultProtocolSwapFeeBalance"]) + Decimal(
                    token["vaultProtocolYieldFeeBalance"]
                )
                fees_controller = Decimal(token["controllerProtocolFeeBalance"])
                if fees_vault > 0 or fees_controller > 0:
                    # TODO: confirm onchain
                    # VaultExplorer.getAggregateSwapFeeAmount(pool, token)
                    # VaultExplorer.getAggregateYieldFeeAmount(pool, token)
                    # assert fees_controller == fees_controller_onchain
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
                    if not ProtocolFeeSweeper.functions.isApprovedProtocolFeeBurner(
                        designated_burner
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
                        sweep_func_name = (
                            "sweepProtocolFeesForToken"
                            # "sweepProtocolFeesForWrappedToken"
                            if token_is_erc4626
                            else "sweepProtocolFeesForToken"
                        )
                        print(
                            f"ProtocolFeeSweeper({sweeper}).{sweep_func_name}({to_checksum_address(pool['address'])},{to_checksum_address(token['address'])},{int(Decimal(potential)* (Decimal(1) - SLIPPAGE)* Decimal('1e6'))},{deadline},{designated_burner})"
                        )
                        unsigned_tx = getattr(
                            ProtocolFeeSweeper.functions, sweep_func_name
                        )(
                            to_checksum_address(pool["address"]),
                            to_checksum_address(token["address"]),
                            int(
                                Decimal(potential)
                                * (Decimal(1) - SLIPPAGE)
                                * Decimal("1e6")
                            ),
                            deadline,
                            (
                                ZERO_ADDRESS
                                if token["address"] == target_token
                                else designated_burner
                            ),
                        ).build_transaction(
                            {
                                "from": Bot.address,
                                "nonce": drpc.eth.get_transaction_count(Bot.address),
                                "maxFeePerGas": max_gas_price,
                                "maxPriorityFeePerGas": max_priority_fee_optimal,
                            }
                        )
                        print("tx: ", end="")
                        pprint(unsigned_tx)
                        signed_tx = drpc.eth.account.sign_transaction(
                            unsigned_tx, Bot.key
                        )
                        if broadcast:
                            try:
                                tx_hash = drpc.eth.send_raw_transaction(
                                    signed_tx.rawTransaction
                                )
                                drpc.eth.wait_for_transaction_receipt(tx_hash)
                            except Exception as e:
                                print(f"!!! tx failed: {e}\n")
                                continue
                            print("tx hash:", tx_hash.hex())
                            if (
                                token["address"] != target_token
                                or asset_address != target_token
                            ):
                                print("waiting for cooldown...")
                                sleep(ORDER_COOLDOWN)
                        print("\n")
                    except (ContractLogicError, ValueError) as e:
                        if "data" in dir(e):
                            if "0xd0c1b3cf" in e.data:
                                # OrderHasUnexpectedStatus
                                _add_to_payload(
                                    DesignatedBurner,
                                    payload_unstuck_tokens,
                                    asset_address,
                                    designated_burner,
                                )
                                continue
                        if "message" in dir(e):
                            if "0xd0c1b3cf" in e.message:
                                # OrderHasUnexpectedStatus
                                _add_to_payload(
                                    DesignatedBurner,
                                    payload_unstuck_tokens,
                                    asset_address,
                                    designated_burner,
                                )
    if len(payload_unstuck_tokens["transactions"]) > 0:
        with open(f"MaxiOps/v3_fees/unstuck_tokens_{chain}.json", "w") as f:
            json.dump(payload_unstuck_tokens, f, indent=2)
            f.write("\n")
    else:
        # delete old file if present
        try:
            os.remove(f"MaxiOps/v3_fees/unstuck_tokens_{chain}.json")
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    report = {}
    for chain in CONFIG:
        report[chain] = {"n_pools": 0, "total_potential": 0, "usdc_collectable": []}
        s = Subgraph(chain)
        prices = get_prices(chain)
        get_pools(chain, broadcast=False)
    pprint(report)
    print(
        "total total_potential:",
        sum([chain["total_potential"] for chain in report.values()]),
    )
