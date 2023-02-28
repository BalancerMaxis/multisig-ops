import pandas as pd
from dotmap import DotMap
from web3 import Web3
import requests
import json

try:
    from brownie import chain
except ImportError:
    print(
        "Warning.  Can't load brownie module in addresses.py.  get_registry() assumes mainnet, use get_registry_by_chain_id()")
    chain = DotMap({"id": 1})


def monorepo_addys_by_chain(chain_name):
    monorepo_addresses = {}
    response = requests.get(
        f"https://raw.githubusercontent.com/balancer-labs/balancer-v2-monorepo/master/pkg/deployments/addresses/{chain_name}.json")
    data = response.json()
    for address, info in data.items():
        monorepo_addresses[info["name"]] = address
    return monorepo_addresses


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
MANAGED_CHAINS = {
    "mainnet": 1,
    "polygon": 137,
    "arbitrum": 42161,
    "optimism": 10,
    "gnosis": 100
}

ADDRESSES_ETH = {
    "zero": "0x0000000000000000000000000000000000000000",
    # the wallets listed here are looped over by scout and checked for all treasury tokens
    "balancer": {
        "multisigs": {
            "lm": "0xc38c5f97B34E175FFd35407fc91a937300E33860",
            "dao": "0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f",
            "fees": "0x7c68c42De679ffB0f16216154C996C354cF1161B",
            "feeManager": "0xf4A80929163C5179Ca042E1B292F5EFBBE3D89e6",
            "karpatkey": "0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89",
            "emergency": "0xA29F61256e948F3FB707b4b3B138C5cCb9EF9888",
            "maxi_ops": "0x166f54F44F271407f24AA1BE415a730035637325"
        },
        "signers": {
            "maxis": {
                "solarcurve": "0x512fce9B07Ce64590849115EE6B32fd40eC0f5F3",
                "zendragon": "0x7c2eA10D3e5922ba3bBBafa39Dc0677353D2AF17",
                "zekraken": "0xafFC70b81D54F229A5F50ec07e2c76D2AAAD07Ae",
                "mikeb": "0xc4591c41e01a7a654B5427f39Bbd1dEe5bD45D1D",
                "xeonus": "0x7019Be4E4eB74cA5F61224FeAf687d2b43998516",
                "danko": "0x200550cAD164E8e0Cb544A9c7Dc5c833122C1438",
                "tritium": "0xcf4fF1e03830D692F52EB094c52A5A6A2181Ab3F"
            },
            "blabs_ops": {
                "Jeff": "0xBEf33200077A2A2AC3613aB92488b41FFc39AcE2",
                "Markus": "0xCae6f77a6cf4C952BF36793D91519fb4Ae86C264",
                "Mike": "0x91f4Df13350083eDb30515019cF527C6b0490c54",
                "Nico": "0x815d654E930E840D0E0Ee1B18FFc8Fb4ddA4c6B3",
                "Fernando": "0xbbF0Ae5195444264364CA7eb7E3BB1971B4c3eCb"
            }
        },
        "deployers": {
            "solarcurve": "0x6409C2C1aC1B26aaaEF982572efd38412075586D",
            "zendragon": "0x854B004700885A61107B458f11eCC169A019b764",
            "mikeb": "0xc4591c41e01a7a654b5427f39bbd1dee5bd45d1d",
            "tritium": "0x53a806789BBfd366d9dEB9Cbe5d622089e845fdb"
        },
        "vault": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
        "gauge_factory": "0x4E7bBd911cf1EFa442BC1b2e9Ea01ffE785412EC",
        "veBAL": "0xC128a9954e6c874eA3d62ce62B468bA073093F25",
        "minter": "0x239e55F427D44C3cc793f49bFB507ebe76638a2b",
        "gauge_controller": "0xC128468b7Ce63eA702C1f104D55A2566b13D3ABD",
        "authorizer_adapter": "0x8F42aDBbA1B16EaAE3BB5754915E0D06059aDd75",
        "authorizer": "0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6", #todo retire
        "Authorizer": "0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6",
        "feeDistributor": "0xD3cf852898b21fc233251427c2DC93d3d604F3BB",
        "ProtocolFeesCollector": "0xce88686553686DA562CE7Cea497CE749DA109f9F",
        "ProtocolFeesWithdrawer": "0x5ef4c5352882b10893b70DbcaA0C000965bd23c5",
        "gauntletFeeSetter": "0xE4a8ed6c1D8d048bD29A00946BFcf2DB10E7923B",
        "maxi_gas_station": "0x2F1901f2A82fcC3Ee9010b809938816B3b06FA6A",
        "poolRecoveryHelper": "0x1b300C86980a5195bCF49bD419A068D98dC133Db",  #https://github.com/balancer-labs/balancer-v2-monorepo/blob/master/pkg/deployments/tasks/20221123-pool-recovery-helper/output/mainnet.json
    },
    "tokens": {
        "bb_a_usd": "0xa13a9247ea42d743238089903570127dda72fe44",
        "FARM": "0xa0246c9032bC3A600820415aE600c6388619A14D",
        "BADGER": "0x3472A5A71965499acd81997a54BBA8D852C6E53d",
        "DIGG": "0x798D1bE841a82a273720CE31c822C61a67a601C3",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "aUSDC": "0xBcca60bB61934080951369a648Fb03DF4F96263C",
        "aUSDT": "0x3Ed3B47Dd13EC9a98b44e6204A523E766B225811",
        "aFEI": "0x683923dB55Fead99A79Fa01A27EeC3cB19679cC3",
        "cUSDC": "0x39aa39c021dfbae8fac545936693ac917d5e7563",
        "cDAI": "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643",
        "cETH": "0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5",
        "DUSD": "0x5BC25f649fc4e26069dDF4cF4010F9f706c23831",
        "alUSD": "0xBC6DA0FE9aD5f3b0d58160288917AA56653660E9",
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "MIM": "0x99D8a9C45b2ecA8864373A26D1459e3Dff1e17F3",
        "FRAX": "0x853d955aCEf822Db058eb8505911ED77F175b99e",
        "aFRAX": "0xd4937682df3C8aEF4FE912A96A74121C0829E664",
        "FEI": "0x956F47F50A910163D8BF957Cf5846D573E7f87CA",
        "CRV": "0xD533a949740bb3306d119CC777fa900bA034cd52",
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "aWBTC": "0x9ff58f4fFB29fA2266Ab25e75e2A8b3503311656",
        "renBTC": "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D",
        "sBTC": "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6",
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "SUSHI": "0x6b3595068778dd592e39a122f4f5a5cf09c90fe2",
        "GTC": "0xDe30da39c46104798bB5aA3fe8B9e0e1F348163F",
        "xSUSHI": "0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272",
        "COMP": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
        "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
        "stkAAVE": "0x4da27a545c0c5B758a6BA100e3a049001de870f5",
        "SPELL": "0x090185f2135308bad17527004364ebcc2d37e5f6",
        "ALCX": "0xdbdb4d16eda451d0503b854cf79d55697f90c8df",
        "FXS": "0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0",
        "CVX": "0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B",
        "cvxCRV": "0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7",
        "EURS": "0xdB25f211AB05b1c97D595516F45794528a807ad8",
        "FTM": "0x4E15361FD6b4BB609Fa63C81A2be19d873717870",
        "BAL": "0xba100000625a3754423978a60c9317c58a424e3D",
        "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
        "AURA": "0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF",
        "AURABAL": "0x616e8BfA43F920657B3497DBf40D6b1A02D4608d",
        "ANGLE": "0x31429d1856aD1377A8A0079410B297e1a9e214c2",
        "ENS": "0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72",
        "RETH": "0xae78736Cd615f374D3085123A210448E74Fc6393",
    },
    "helpers": {
        "balance_checker": "0xe92261c2D64C363109c36a754A87107142e61b72",
    },
    "compound": {
        "comptroller": "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B",
    },
    "across": {
        "spoke_pool": "0x4D9079Bb4165aeb4084c526a32695dCfd2F77381"
    },
    "aave": {
        "incentives_controller": "0xd784927Ff2f95ba542BfC824c8a8a98F3495f6b5",
        "aave_lending_pool_v2": "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
        "data_provider": "0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d",
        "price_oracle_v2": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    },
    "cow": {
        "vault_relayer": "0xC92E8bdf79f0507f65a392b0ab4667716BFE0110",
        "settlement": "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
    },
    "convex": {
        "cvxCRV_rewards": "0x3Fe65692bfCD0e6CF84cB1E7d24108E434A7587e",
        "crv_depositor": "0x8014595F2AB54cD7c604B00E9fb932176fDc86Ae",
        "vlCvxExtraRewardDistribution": "0xDecc7d761496d30F30b92Bdf764fb8803c79360D",
        "booster": "0xF403C135812408BFbE8713b5A23a04b3D48AAE31",
        "claim_zap": "0x92Cf9E5e4D1Dfbf7dA0d2BB3e884a68416a65070",
        "vlCVX": "0xD18140b4B819b895A3dba5442F959fA44994AF50",
        "frax": {
            "booster": "0x569f5B842B5006eC17Be02B8b94510BA8e79FbCa",
            "pool_registry": "0x41a5881c17185383e19Df6FA4EC158a6F4851A69",
        },
    },
    "votium": {
        "bribe": "0x19BBC3463Dd8d07f55438014b021Fb457EBD4595",
        "multiMerkleStash": "0x378Ba9B73309bE80BF4C2c027aAD799766a7ED5A",
    },

    "uniswap": {
        "factoryV3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
        "NonfungiblePositionManager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
        "routerV2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "routerV3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "factoryV2": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
    },
    "sushiswap": {
        "routerV2": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
        "factoryV2": "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac",
    },
    "curve": {
        "provider": "0x0000000022D53366457F9d5E68Ec105046FC4383",
        "factory": "0x0959158b6040D32d04c301A72CBFD6b39E21c9AE",
    },

    "hidden_hand": {
        "bribe_vault": "0x9DDb2da7Dd76612e0df237B89AF2CF4413733212",
        "tokenmak_briber": "0x7816b3D0935D668bCfc9A4aaB5a84EBc7fF320cf",
        "balancer_briber": "0x7Cdf753b45AB0729bcFe33DC12401E55d28308A9",
        "rewards_distributor": "0x0b139682D5C9Df3e735063f46Fb98c689540Cf3A",
        "aura_briber": "0x642c59937A62cf7dc92F70Fd78A13cEe0aa2Bd9c",
        "frax_briber": "0x123683885310851Ca29e83AE3FF3e2490D4420Cd",
    },
    "chainlink": {
        "feed_registry": "0x47Fb2585D2C56Fe188D0E6ec628a38b74fCeeeDf",
        "keeper_registry": "0x02777053d6764996e594c3E88AF1D58D5363a2e6",
        "keeper_registrar": "0xDb8e8e2ccb5C033938736aa89Fe4fa1eDfD15a1d",
    },
    "across_bridge": {
        "hub_pool": "0x6Bb9910c5529Cb3b32c4f0e13E8bC38F903b2534",
    },
    "maker": {
        "proxy_registry": "0x4678f0a6958e4D2Bc4F1BAF7Bc52E8F3564f3fE4",
    },
    "gnosis": {
        "sign_message_lib": "0xA65387F16B013cf2Af4605Ad8aA5ec25a2cbA3a2",
    },
    "aura": {
        "wrapper": "0x68655AD9852a99C87C0934c7290BB62CFa5D4123",
        "depositor": "0xeAd792B55340Aa20181A80d6a16db6A0ECd1b827",
        "aurabal_staking": "0xC47162863a12227E5c3B0860715F9cF721651C0c",
        "aurabal_rewards": "0x5e5ea2048475854a5702F5B8468A51Ba1296EFcC",
        "vlAURA": "0x3Fa73f1E5d8A792C80F426fc8F84FBF7Ce9bBCAC",
        "merkle_drop": "0x45EB1A004373b1D8457134A2C04a42d69D287724",
        "booster": "0x7818A1DA7BD1E64c199029E86Ba244a9798eEE10",
        "claim_zap": "0x623B83755a39B12161A63748f3f595A530917Ab2",
        "extra_rewards_distributor": "0xa3739b206097317c72ef416f0e75bb8f58fbd308",
        "gauge_migrator": "0x7954bcDce86e86BeE7b1dEff48c3a0b9BCCe578B",
    },
    "ens": {
        "registry": "0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e",
        "public_resolver": "0x4976fb03C32e5B8cfe2b6cCB31c09Ba78EBaBa41",
    },
    "euler": {
        "euler": "0x27182842E098f60e3D576794A5bFFb0777E025d3",
        "euler_markets": "0x3520d5a913427E6F0D6A83E07ccD4A4da316e4d3",
    },
}

ADDRESSES_POLYGON = {
    "zero": "0x0000000000000000000000000000000000000000",
    "balancer": {
        "multisigs": {
            "lm": "0xc38c5f97B34E175FFd35407fc91a937300E33860",
            "dao": "0xeE071f4B516F69a1603dA393CdE8e76C40E5Be85",
            "fees": "0x7c68c42De679ffB0f16216154C996C354cF1161B",
            "feeManager": "0x7c68c42De679ffB0f16216154C996C354cF1161B",  ## fees is feeManager on Polygon
            "emergency": "0x3c58668054c299bE836a0bBB028Bee3aD4724846"
        },
        "authorizer": "0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6",
        "Authorizer": "0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6", #TODO retire
        "poolRecoveryHelper": "0x495F696430F4A51F7fcB98FbE68a9Cb7A07fB1bA",  #https://github.com/balancer-labs/balancer-v2-monorepo/blob/master/pkg/deployments/tasks/20221123-pool-recovery-helper/output/polygon.json

    },
    "tokens": {
        "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "WMATIC": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
        "WETH": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
        "BAL": "0x9a71012B13CA4d3D0Cdc72A177DF3ef03b0E76A3",
        "WBTC": "0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6"

    },
    "across": {
        "spoke_pool": "0x69B5c72837769eF1e7C164Abc6515DcFf217F920"
    },
}

ADDRESSES_ARBITRUM = {
    "zero": "0x0000000000000000000000000000000000000000",
    "registry_v2": "0xdc602965F3e5f1e7BAf2446d5564b407d5113A06",
    "registryAccessControl": "0x6847a17C4AC30AFd24FDcb2422DA01207C480a79",
    "EmissionControl": "0x78418681f9ed228d627f785fb9607ed5175518fd",
    "wallets": {},
    "balancer": {
        "multisigs": {
            "lm": "0xc38c5f97B34E175FFd35407fc91a937300E33860",
            "dao": "0xaF23DC5983230E9eEAf93280e312e57539D098D0",
            "fees": "0x7c68c42De679ffB0f16216154C996C354cF1161B",
            "feeManager": "0x7c68c42De679ffB0f16216154C996C354cF1161B", # fees is feeManager on Arbitrum
            "emergency": "0xf404C5a0c02397f0908A3524fc5eb84e68Bbe60D"
        },
        "authorizer": "0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6",
        "authorizer": "0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6", # TODO retire
        "poolRecoveryHelper": "0xb5e56CC3d2e38e53b1166175C59e921A37cDC1E2"  #https://github.com/balancer-labs/balancer-v2-monorepo/blob/master/pkg/deployments/tasks/20221123-pool-recovery-helper/output/arbitrum.json
    },
    "tokens": {
        "BADGER": "0xBfa641051Ba0a0Ad1b0AcF549a89536A0D76472E",
        "WBTC": "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f",
        "USDC": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
        "CRV": "0x11cdb42b0eb46d95f990bedd4695a6e3fa034978",
        "SUSHI": "0xd4d42f0b6def4ce0383636770ef773390d85c61a",
        "renBTC": "0xdbf31df14b66535af65aac99c32e9ea844e14501",
        "WETH": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
        "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
    },
    "coingecko_tokens": {
        "badger-dao": "0xbfa641051ba0a0ad1b0acf549a89536a0d76472e",
        "wrapped-bitcoin": "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f",
        "curve-dao-token": "0x11cdb42b0eb46d95f990bedd4695a6e3fa034978",
        "sushi": "0xd4d42f0b6def4ce0383636770ef773390d85c61a",
        "renbtc": "0xdbf31df14b66535af65aac99c32e9ea844e14501",
        "weth": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
        "usdx": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
    },
    "across": {
        "spoke_pool": "0xB88690461dDbaB6f04Dfad7df66B7725942FEb9C"
    },
    "sushi": {"router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"},
    "swapr": {"router": "0x530476d5583724A89c8841eB6Da76E7Af4C0F17E"},
    "arbitrum_node": "0x00000000000000000000000000000000000000C8",
    "arbitrum_gateway_router": "0x5288c571Fd7aD117beA99bF60FE0846C4E84F933",
}

ADDRESSES_OPTIMISM = {
    "zero": "0x0000000000000000000000000000000000000000",
    "balancer": {
        "multisigs": {
            "lm": "0x09Df1626110803C7b3b07085Ef1E053494155089",
            "dao": "0x043f9687842771b3dF8852c1E9801DCAeED3f6bc",
            "fees": "0x09Df1626110803C7b3b07085Ef1E053494155089",  ## fees is LM on Optimism
            "feeManager": "0x09Df1626110803C7b3b07085Ef1E053494155089",  ## fees is LM on Optimism
            "emergency": "0xd4c87b33afcE39F1E3F4aF1ce8fFFF7241d9128B"
        },
        "authorizer": "0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6",
        "Authorizer": "0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6", # TODO retire

        "poolRecoveryHelper": "0x26743984e3357eFC59f2fd6C1aFDC310335a61c9" # https://github.com/balancer-labs/balancer-v2-monorepo/blob/master/pkg/deployments/tasks/20221123-pool-recovery-helper/output/optimism.json
    },
    "tokens": {},
}
ADDRESSES_GOERLI = {
    "zero": "0x0000000000000000000000000000000000000000",
    # the wallets listed here are looped over by scout and checked for all treasury tokens
    "balancer": {
        "signers": {
            "maxis": {
                "solarcurve": "0x512fce9B07Ce64590849115EE6B32fd40eC0f5F3",
                "zendragon": "0x7c2eA10D3e5922ba3bBBafa39Dc0677353D2AF17",
                "zekraken": "0xafFC70b81D54F229A5F50ec07e2c76D2AAAD07Ae",
                "mikeb": "0xc4591c41e01a7a654B5427f39Bbd1dEe5bD45D1D",
                "xeonus": "0x7019Be4E4eB74cA5F61224FeAf687d2b43998516",
                "danko": "0x200550cAD164E8e0Cb544A9c7Dc5c833122C1438",
                "tritium": "0xcf4fF1e03830D692F52EB094c52A5A6A2181Ab3F"
            },
        },
        "multisigs": {
            "maxi_ops": "0x040E995520F92F96142d1a76c16D4af21A2eFDE7",
            "blab_ops": ZERO_ADDRESS
        }
    },
    "chainlink": {
        "feed_registry": "0x47Fb2585D2C56Fe188D0E6ec628a38b74fCeeeDf",
        "keeper_registry": "0xE16Df59B887e3Caa439E0b29B42bA2e7976FD8b2",
        "keeper_registrar": "0x57A4a13b35d25EE78e084168aBaC5ad360252467",
    },
    "tokens": {
        "LINK": "0x326C977E6efc84E512bB9C30f76E30c160eD06FB"
    }
}

ADDRESSES_GNOSIS = {
    "zero": "0x0000000000000000000000000000000000000000",
    "balancer": dict(monorepo_addys_by_chain("gnosis"))
}
ADDRESSES_GNOSIS["balancer"]["multisigs"] = dict({
    "emergency": "0xd6110A7756080a4e3BCF4e7EBBCA8E8aDFBC9962",
    "dao": "0x2a5AEcE0bb9EfFD7608213AE1745873385515c18",
    # All maxi operations concentrated into 1 multisig
    "lm": "0x14969B55a675d13a1700F71A37511bc22D90155a",
    "fees": "0x14969B55a675d13a1700F71A37511bc22D90155a",
    "feeManager": "0x14969B55a675d13a1700F71A37511bc22D90155a",
    "blabs_ops": ZERO_ADDRESS
})

OTHER_STUFF = {
    "ETH": {
        "chainlink_upkeeps": {
            "maxi_gas_station": "62602467182204477380138952081172885895406053754821061796893606503759482417757"
        }
    }
}


def checksum_address_dict(addresses):
    """
    convert addresses to their checksum variant taken from a (nested) dict
    """
    checksummed = {}
    for k, v in addresses.items():
        if isinstance(v, str):
            checksummed[k] = Web3.toChecksumAddress(v)
        elif isinstance(v, dict):
            checksummed[k] = checksum_address_dict(v)
        else:
            print(k, v, "formatted incorrectly")
    return checksummed


with open("helpers/chaindata.json") as chaindata:
    chain_ids = json.load(chaindata)

registry = DotMap(
    {
        "eth": checksum_address_dict(ADDRESSES_ETH),
        "poly": checksum_address_dict(ADDRESSES_POLYGON),
        "arbitrum": checksum_address_dict(ADDRESSES_ARBITRUM),
        "op": checksum_address_dict(ADDRESSES_OPTIMISM),
        "gnosis": checksum_address_dict(ADDRESSES_GNOSIS),
        "goerli": checksum_address_dict(ADDRESSES_GOERLI)
    }
)


def flat_callers_by_chain(chain_name):
    reg = get_registry_by_chain_id(MANAGED_CHAINS[chain_name])
    # Build a list of callers out of the multisigs and the other balancer addresses
    callers = dict(reg.balancer.multisigs)
    for name, value in reg.balancer.items():
        if type(value) is str:
            if name in callers.keys():
                print(
                    f"WARNING: Collision between {name}:{value} which is already in the list with value {callers[name]}")
            callers[name] = value
    return callers


def get_registry_by_chain_id(chain_id):
    if chain_id == 1:
        return registry.eth
    elif chain_id == 137:
        return registry.poly
    elif chain_id == 56:
        return registry.bsc
    elif chain_id == 42161:
        return registry.arbitrum
    elif chain_id == 250:
        return registry.ftm
    elif chain_id == 10:
        return registry.op
    elif chain_id == 42:
        return registry.kovan
    elif chain_id == 5:
        return registry.goerli
    elif chain_id == 100:
        return registry.gnosis


def get_registry():
    if chain.id == 1:
        return registry.eth
    elif chain.id == 137:
        return registry.poly
    elif chain.id == 56:
        return registry.bsc
    elif chain.id == 42161:
        return registry.arbitrum
    elif chain.id == 250:
        return registry.ftm
    elif chain.id == 10:
        return registry.op
    elif chain.id == 42:
        return registry.kovan
    elif chain.id == 5:
        return registry.goerli
    elif chain.id == 100:
        return registry.gnosis


r = get_registry()

# flatten nested dicts and invert the resulting key <-> value
# this allows for reversed lookup of an address
df = pd.json_normalize(registry, sep="_")
reverse = df.T.reset_index().set_index(0)["index"].to_dict()
