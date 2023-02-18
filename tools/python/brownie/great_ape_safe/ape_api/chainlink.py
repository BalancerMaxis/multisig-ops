from brownie import interface, chain
from helpers.addresses import r


class Chainlink:
    def __init__(self, safe):
        self.safe = safe

        # contracts
        self.link = self.safe.contract(r.tokens.LINK, interface.ILinkToken)
        self.keeper_registry = self.safe.contract(
            r.chainlink.keeper_registry, interface.IKeeperRegistry
        )
        self.keeper_registry_v1_1 = self.safe.contract(
            r.chainlink.keeper_registry_v1_1, interface.IKeeperRegistry
        )
        self.keeper_registrar = self.safe.contract(
            r.chainlink.keeper_registrar, from_explorer=True
        )

    def register_upkeep(
        self, name, contract_addr, gas_limit, link_mantissa, admin_addr=None
    ):
        """
        ref: https://github.com/smartcontractkit/keeper/blob/master/contracts/UpkeepRegistrationRequests.sol
        """

        admin_addr = self.safe.address if not admin_addr else admin_addr
        if chain.id == 4:  # gorli
            data = self.keeper_registrar.register.encode_input(
                name,  # string memory name,
                b"",  # bytes calldata encryptedEmail,
                contract_addr,  # address upkeepContract,
                gas_limit,  # uint32 gasLimit,
                admin_addr,  # address adminAddress,
                b"",  # bytes calldata checkData,
                b"",  # offchainConfig (bytes)
                link_mantissa,  # uint96 amount,
                self.safe.address,  # address sender,
            )
        else: # tested on mainnet
            data = self.keeper_registrar.register.encode_input(
                name,  # string memory name,
                b"",  # bytes calldata encryptedEmail,
                contract_addr,  # address upkeepContract,
                gas_limit,  # uint32 gasLimit,
                admin_addr,  # address adminAddress,
                b"",  # bytes calldata checkData,
                link_mantissa,  # uint96 amount,
                42,  # source (uint8)
                self.safe.address,  # address sender,
            )


        self.link.transferAndCall(self.keeper_registrar, link_mantissa, data)
