from bal_addresses import AddrBook
from bal_tools.safe_tx_builder import SafeTxBuilder, SafeContract
from bal_tools.utils import get_abi
from decimal import Decimal, ROUND_DOWN
import pandas as pd

GNOSIS_OMNIBRIDGE = "0x88ad09518695c6c3712AC10a214bE5109a655671"
GNOSIS_BAL_ADDRESS = "0x7eF541E2a22058048904fE5744f9c7E4C57AF717"


def to_wei(amount):
    return int(
        (Decimal(amount) * Decimal("1e18")).to_integral_value(rounding=ROUND_DOWN)
    )


airdrop = pd.read_csv("ZenBetaAirdrop.csv").dropna(subset=["Address"])
mainnet_recipients = airdrop[
    (airdrop["Pay on mainnet"] == "Yes")
    & (airdrop["BAL award if program ended today"] > 0)
]
gnosis_recipients = airdrop[
    (airdrop["Pay on mainnet"] != "Yes")
    & (airdrop["BAL award if program ended today"] > 0)
]
bridge_to_gnosis = to_wei(gnosis_recipients["BAL award if program ended today"].sum())


### mainnet transactions
mainnet_builder = SafeTxBuilder("multisigs/lm", chain_name="mainnet")
bal = SafeContract("tokens/BAL", abi_file_path="abi/ERC20.json")
omnibridge = SafeContract(GNOSIS_OMNIBRIDGE, abi_file_path="abi/omnibridge.json")

for _, row in mainnet_recipients.iterrows():
    bal.transfer(row["Address"], to_wei(row["BAL award if program ended today"]))

bal.approve(GNOSIS_OMNIBRIDGE, bridge_to_gnosis)
omnibridge.relayTokens(bal.address, AddrBook("gnosis").multisigs.lm, bridge_to_gnosis)

mainnet_builder.output_payload("transactions/ZenAirdropMainnet.json")


### gnosis transactions
gnosis_builder = SafeTxBuilder("multisigs/lm", chain_name="gnosis")
bal = SafeContract(GNOSIS_BAL_ADDRESS, get_abi("ERC20"))

for _, row in gnosis_recipients.iterrows():
    bal.transfer(row["Address"], to_wei(row["BAL award if program ended today"]))

gnosis_builder.output_payload("transactions/ZenAirdropGnosis.json")
