import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pprint import pprint
from time import sleep

from bal_addresses import AddrBook, to_checksum_address
from bal_addresses.addresses import ZERO_ADDRESS
from bal_tools import Subgraph
from requests import Session
from requests.adapters import HTTPAdapter, Retry
from web3 import Web3


CONFIG = json.load(open("action-scripts/v3_fee_config.json"))
ORDER_COOLDOWN = 60 * 5  # 5 minutes
SLIPPAGE = Decimal("0.005")  # 50bips slippage
NULL = None
OMNI_MSIG = "0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e"
ADAPTER = HTTPAdapter(
    pool_connections=20,
    pool_maxsize=20,
    max_retries=Retry(
        # 400 and 404 have special meaning in the context of this api:
        # 400: error finding the price
        # 404: no liquidity was found
        # ref: https://docs.cow.fi/cow-protocol/reference/apis/orderbook
        total=10,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504, 520],
    ),
)
COW_API_SESSION = Session()
COW_API_SESSION.mount("https://", ADAPTER)


def get_prices(chain: str):
    return dict(
        [
            (token["address"], Decimal(token["price"]))
            for token in s.fetch_graphql_data(
                "apiv3", "get_prices", {"chains": [chain.upper()]}
            )["tokenGetCurrentPrices"]
        ]
    )


def _execute_tx(Contract, contract_name, func_name, params, Bot, drpc, broadcast):
    print(f"{contract_name}.({Contract.address}).{func_name}({params})")

    # sort out gas price and priority fee
    fee_data = drpc.eth.fee_history(1, "latest")
    max_gas_price = int(CONFIG[chain]["max_gas_price"])
    max_priority_fee = int(CONFIG[chain]["max_priority_fee"])
    if fee_data.baseFeePerGas[-1] > max_gas_price:
        print(f"!!! base fee too high ({fee_data.baseFeePerGas[-1]}); skipping")
        return
    try:
        max_priority_fee_latest = fee_data.reward[0][0]
        if max_priority_fee_latest > 0:
            max_priority_fee_optimal = min(max_priority_fee, max_priority_fee_latest)
    except:
        max_priority_fee_optimal = max_priority_fee

    # build tx
    unsigned_tx = getattr(Contract.functions, func_name)(*params).build_transaction(
        {
            "from": Bot.address,
            "nonce": drpc.eth.get_transaction_count(Bot.address),
            "maxFeePerGas": max_gas_price,
            "maxPriorityFeePerGas": max_priority_fee_optimal,
        }
    )
    print("tx: ", end="")
    pprint(unsigned_tx)

    # sign tx
    signed_tx = drpc.eth.account.sign_transaction(unsigned_tx, Bot.key)
    if broadcast:
        try:
            tx_hash = drpc.eth.send_raw_transaction(signed_tx.rawTransaction)
            drpc.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            print(f"!!! tx failed: {e}")
            return
        print("tx hash:", tx_hash.hex())


def _can_cancel_order(DesignatedBurner, asset_address):
    if DesignatedBurner.functions.getOrderStatus(
        to_checksum_address(asset_address)
    ).call() not in [0, 2]:
        # OrderStatus is neither NonExistent nor Filled
        # can thus be cancelled as soon as it expires
        if DesignatedBurner.functions.getOrder(
            to_checksum_address(asset_address)
        ).call()[5] < int(datetime.timestamp(datetime.now(timezone.utc))):
            return True
    return False


def _unstuck_token(DesignatedBurner, Bot, drpc, asset_address, broadcast):
    print("!!! token stuck in burner; unstucking...")
    try:
        _execute_tx(
            DesignatedBurner,
            "DesignatedBurner",
            "cancelOrder",
            [to_checksum_address(asset_address), OMNI_MSIG],
            Bot,
            drpc,
            broadcast,
        )
    except:
        print("!!! token can neither be burned nor cancelled")


def _can_get_quote(chain: str, asset_address: str) -> bool:
    chain_name = {
        "sepolia": "sepolia",
        "mainnet": "mainnet",
        "gnosis": "xdai",
        "arbitrum": "arbitrum_one",
        "base": "base",
    }[chain]
    r = COW_API_SESSION.get(
        f"https://api.cow.fi/{chain_name}/api/v1/token/{to_checksum_address(asset_address)}/native_price"
    )
    if r.status_code == 200:
        if float(r.json().get("price")) > 0:
            return True


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
    burner = (
        AddrBook(chain).search_unique("mimic/fee_burner").address
        if chain == "avalanche"
        else AddrBook(chain).search_unique("20250530-v3-cow-swap-fee-burner-v2").address
    )
    erc4626_burner = (
        burner
        if chain == "avalanche"
        else AddrBook(chain)
        .search_unique("20250530-v3-erc4626-cow-swap-fee-burner-v2")
        .address
    )
    VaultExplorer = drpc.eth.contract(
        address=AddrBook(chain)
        .search_unique("20250407-v3-vault-explorer-v2/VaultExplorer")
        .address,
        abi=json.load(open("action-scripts/abis/IVaultExplorer.json")),
    )
    ProtocolFeeController = drpc.eth.contract(
        address=AddrBook(chain)
        .search_unique("20250214-v3-protocol-fee-controller-v2/ProtocolFeeController")
        .address,
        abi=json.load(open("action-scripts/abis/IProtocolFeeController.json")),
    )
    threshold = Decimal(CONFIG[chain]["usdc_threshold"])
    for pool in s.fetch_graphql_data("apiv3", "get_pools", {"chain": chain.upper()})[
        "poolGetPools"
    ]:
        if pool["protocolVersion"] != 3:
            continue
        report[chain]["n_pools"] += 1
        print(
            f"\n\nchecking for pending fees on {chain}:{pool['address']} ({pool['symbol']})..."
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
                if not ProtocolFeeSweeper.functions.isApprovedProtocolFeeBurner(
                    designated_burner
                ).call():
                    print("!!! burner not approved (yet); skipping")
                    continue
                DesignatedBurner = drpc.eth.contract(
                    address=to_checksum_address(designated_burner),
                    abi=json.load(open("action-scripts/abis/ICowSwapFeeBurner.json")),
                )
                balance = Asset.functions.balanceOf(designated_burner).call()
                if balance > 0:
                    if _can_cancel_order(DesignatedBurner, asset_address):
                        _unstuck_token(
                            DesignatedBurner, Bot, drpc, asset_address, broadcast
                        )
                        if broadcast == False:
                            # do not try to burn fees; cancellation has not been broadcasted
                            continue
                    else:
                        print("!!! token still has an open order; skipping")
                        continue
                fees_vault = Decimal(token["vaultProtocolSwapFeeBalance"]) + Decimal(
                    token["vaultProtocolYieldFeeBalance"]
                )
                fees_controller = Decimal(token["controllerProtocolFeeBalance"])
                if fees_vault > 0 or fees_controller > 0:
                    decimals = Asset.functions.decimals().call()
                    # confirm fees onchain
                    swap_fees_vault_onchain = Decimal(
                        VaultExplorer.functions.getAggregateSwapFeeAmount(
                            to_checksum_address(pool["address"]),
                            to_checksum_address(token["address"]),
                        ).call()
                    ) / Decimal(10**decimals)
                    # assert swap_fees_onchain == Decimal(
                    #     token["vaultProtocolSwapFeeBalance"]
                    # )
                    yield_fees_vault_onchain = Decimal(
                        VaultExplorer.functions.getAggregateYieldFeeAmount(
                            to_checksum_address(pool["address"]),
                            to_checksum_address(token["address"]),
                        ).call()
                    ) / Decimal(10**decimals)
                    # assert yield_fees_onchain == Decimal(
                    #     token["vaultProtocolYieldFeeBalance"]
                    # )
                    fees_vault_onchain = (
                        swap_fees_vault_onchain + yield_fees_vault_onchain
                    )
                    if fees_vault != fees_vault_onchain:
                        # subgraph is running behind; skip for now
                        print("!!! subgraph is running behind; skipping")
                        continue
                    fees_controller_onchain_all = (
                        ProtocolFeeController.functions.getProtocolFeeAmounts(
                            to_checksum_address(pool["address"])
                        ).call()
                    )
                    # find correct index for token; fees are sorted in token registration order
                    for i, t in enumerate(pool["poolTokens"]):
                        if t["address"].lower() == token["address"].lower():
                            idx = i
                            break
                    else:
                        print(
                            f"!!! cannot find token {token['address']} in pool {pool['address']}, skipping"
                        )
                        continue
                    fees_controller_onchain = fees_controller_onchain_all[
                        idx
                    ] / Decimal(10**decimals)
                    # assert fees_controller_onchain == fees_controller
                    if fees_controller != fees_controller_onchain:
                        # subgraph is running behind; skip for now
                        print("!!! subgraph is running behind; skipping")
                        breakpoint()
                        continue
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
                    print("token:", token["symbol"], token["address"])
                    print("price:", f"${prices[token['address']]}")
                    print("collectable in vault:", fees_vault, token["symbol"])
                    print("sweepable in controller:", fees_controller, token["symbol"])
                    if potential < threshold:
                        print(f"not enough fees to burn; only worth {potential} USDC")
                        continue
                    report[chain]["total_potential"] += potential
                    print("burning for:", potential, "USDC"),

                    deadline = int(
                        datetime.timestamp(
                            datetime.now(timezone.utc) + timedelta(minutes=90)
                        )
                    )
                    if (
                        token["address"].lower()
                        == "0x7788A3538C5fc7F9c7C8A74EAC4c898fC8d87d92".lower()
                    ):
                        # StakedUSDX.redeem() reverts on modifier ensureCooldownOff();
                        # require(cooldownDuration == 0, Errors.OPERATION_NOT_ALLOWED)
                        print("!!! skipping StakedUSDX; has redeem issues...")
                        continue
                    if chain != "avalanche":
                        if not _can_get_quote(chain, asset_address):
                            print(
                                f"!!! {asset_address} cant get quote from cow burner; skipping for now"
                            )
                            continue
                    _execute_tx(
                        ProtocolFeeSweeper,
                        "ProtocolFeeSweeper",
                        "sweepProtocolFeesForToken",
                        [
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
                        ],
                        Bot,
                        drpc,
                        broadcast,
                    )
                    if broadcast:
                        if (
                            token["address"] != target_token
                            or asset_address != target_token
                        ) and chain != "avalanche":
                            print("waiting for cooldown...")
                            sleep(ORDER_COOLDOWN)


if __name__ == "__main__":
    report = {}
    for chain in CONFIG:
        report[chain] = {"n_pools": 0, "total_potential": 0, "usdc_collectable": []}
        s = Subgraph(chain)
        prices = get_prices(chain)
        get_pools(chain, broadcast=True)
    pprint(report)
    print(
        "total total_potential:",
        sum([chain["total_potential"] for chain in report.values()]),
    )
