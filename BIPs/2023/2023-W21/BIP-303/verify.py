from brownie import Contract

from bal_addresses import AddrBook

a = AddrBook("zkevm")

### zkevm.json
a.reversebook["0x2f237e7643a3bF6Ef265dd6FCBcd26a7Cc38dbAa"]
daomsig = "0x2f237e7643a3bF6Ef265dd6FCBcd26a7Cc38dbAa"


a.reversebook["0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6"]

Authorizer = Contract("0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6")
roleList = "0xc286c677f812387602b94d5dee672097cae543d80e175977381fbdbcdb9b2c12, 0x2aa887a92d3d18f30f198214d2c197b7d148bb735c610372199c51c6a4866b86, 0xe67bef3cfb0ba409959647fa3d8ff78b267a1c13f5434c2f32219ced33fec922, 0x8d305e761700b38cf2bc3f9e2c4ad60807e843cf2efd2415b902b1163f8f9a22, 0xb213b9fefdba263a47d6449bab5d563a39489f656d504fd24d5b9efe6fe23a61, 0x6c331c074092fbc25cd1032630ed25155aa5b81afa1d296bf5a0f0e9e0c6e846, 0x5b9fa6724045ae552732087c24c3eabd3d760a41440cf37d3646a5325241b40f, 0xecb7a0b42168ed1b4327ddb3a6fc128facd2fd4c066e2d9d5817452f5f445a4c, 0xca88ea7c3ad439ada200e7ec242c17b97994dda6cc1d6c944b4efbea82b7e479, 0xca1bf022f0a4111e9e6995ddb177d334178b978208cdf454fe8b8a81eaa50b1e, 0x71485a098a59b05ec94c66ce65941514fde1427b10f7a920bef592a077d2e4f1, 0xb8f99692f0cb1e9dbabcb6d9e154bf55ee4fc003eb5e75a94b3acd8c3628ec7e, 0x54d04f96e1384dacfbc4bb06d4876678ad3ba07c255782bd693bc9df4b367e24, 0xe439de626f6f6121ebeb2d7f9b3ad6fdb8b2c645d3b1de4de1d2624bf95aea4b, 0x18d598983407d1a7c8ee21df73bf1fa9f89919b69f6a712b8521f5d82c211609, 0x7dc4d368b1715140a72ae8d3535a67a2a12cf4671cad76b40860d2d66d514303, 0x226f4cdd3b2ef4ab0d183f2b048476bdf13ac41bc5d16b620a5c9801f07284c1, 0xfb4212380dd0e89902957b9e27258f6ca18cb800e3669b8603b6904ac59e98dc, 0x7dc87d34e4d9603c093467dcbbf3a46c73c3cc593d90bd69353bfef0be8e12a4, 0x3ce3b3d8a6d2e5a3432dba62d502f9309c00298258a5c2a68371fca06e6ea0dd, 0xfb08e1536837d0f69d82dc0a71f05d5e9ea8b7cfb7b429091b10dd68dadb2256, 0xb5593fe09464f360ecf835d5b9319ce69900ae1b29d13844b73c250b1f5f92fb, 0xdbc8f1f973e905b408bd874b7b2dd4ac3a8b6d6494b51da5c28de0ec4ac21791"
roleList = roleList.split(", ")
a.reversebook["0x79b131498355daa2cC740936fcb9A7dF76A86223"]
emergencymsig = "0x79b131498355daa2cC740936fcb9A7dF76A86223"
tx = Authorizer.grantRoles(roleList, emergencymsig, {"from": daomsig})
tx.call_trace(expand=True)


a.reversebook["0xf7D5DcE55E6D47852F054697BAB6A1B48A00ddbd"]
"20221123-pool-recovery-helper/PoolRecoveryHelper"
PoolRecoveryHelper = Contract.from_explorer(
    "0xf7D5DcE55E6D47852F054697BAB6A1B48A00ddbd"
)
roleList = "0x2aa887a92d3d18f30f198214d2c197b7d148bb735c610372199c51c6a4866b86, 0xb213b9fefdba263a47d6449bab5d563a39489f656d504fd24d5b9efe6fe23a61, 0xecb7a0b42168ed1b4327ddb3a6fc128facd2fd4c066e2d9d5817452f5f445a4c, 0x71485a098a59b05ec94c66ce65941514fde1427b10f7a920bef592a077d2e4f1, 0xe439de626f6f6121ebeb2d7f9b3ad6fdb8b2c645d3b1de4de1d2624bf95aea4b, 0x226f4cdd3b2ef4ab0d183f2b048476bdf13ac41bc5d16b620a5c9801f07284c1, 0x3ce3b3d8a6d2e5a3432dba62d502f9309c00298258a5c2a68371fca06e6ea0dd"
roleList = roleList.split(", ")
tx = Authorizer.grantRoles(roleList, PoolRecoveryHelper.address, {"from": daomsig})
tx.call_trace(expand=True)

a.reversebook["0xB59Ab49CA8d064E645Bf2c546d9FE6d1d4147a09"]
"multisigs/lm"
lmmsig = "0xB59Ab49CA8d064E645Bf2c546d9FE6d1d4147a09"
roleList = "0xdf1065695aeed28f2f774ad5c0032a5d8fb873b2c325e8204d3ec2076d913779, 0xcf555cc0ffe0f3255e6e21b7f9236c3c9fa8f7bbeb3c8796df9d3b5b6b630f1b, 0x3005acc2387c9b240d98175714c97d50f7215ed66a79cafb014a53b74250b3a7, 0xc5cc9cd4aa2b8c41b752cd191bc035c569522e23523abd0cc53c6a229165589f, 0x4223f854b20ca267ff7b134cf89c74ad7ad53e42dcef38dd11350fa25e3d83ae, 0x30329a0bf89785c711811ca02c5e649b59ef6706cd7e707ff91290a62f22996d, 0xcb96c6dcd233b49f5decb6e39b3a91d415076c7d8c78ef46aad6e1823ba2dfde, 0xf037bfa1f407c134bc46cd288ab93d47b13cd73831c019707c6fed5162cf1b2d, 0xe716f33bb1aed7ca21a3a428a38e0fec5f3ea274a3fa22d8171e5b5e849c7f03, 0xf8e0160362ea0d3bd75a137e0a65022b2a4db29686269ff6e2857f869f477f14, 0xb851a779bb251247ffc9b445a0fac56af908e4560fe43517739bb79e73f94ddc, 0xe3fccd861cb8896c55052a07fa6c8a620343c50e5b7971d6a5ea70a41feb7e93, 0xdc8b557d7b464894c525e5de06257694247b2b789b4948326752177399475439, 0xcd3768eb08cdc2de2d040f74fb351ccbef01df1d042fa8033e12f224ecc27c4d, 0x4133838a02bd2b8ed714d2c6f9b67c9edc60b2a48cdffca2fc4908545c9ea168, 0xe54abf8b88dbe1bc275b3ffd3f7ab1b0ad3541db2664b78940b7fb9c05526bf2, 0xc26e21fc0aba43b199202ad3de0ba39a17c1006c1f7b3791ca2a3b9f86a4f0b9, 0x717d11aa4cee062d5f4a3262a493c6cb8b8d7985b98d3a3fd2f80631feb89968"
roleList = roleList.split(", ")
tx = Authorizer.grantRoles(roleList, lmmsig, {"from": daomsig})
tx.call_trace(expand=True)


a.reversebook["0x4678731DC41142A902a114aC5B2F77b63f4a259D"]
BatchRelayer = Contract.from_explorer("0x4678731DC41142A902a114aC5B2F77b63f4a259D")
roleList = "0x1282ab709b2b70070f829c46bc36f76b32ad4989fecb2fcb09a1b3ce00bbfc30, 0xc149e88b59429ded7f601ab52ecd62331cac006ae07c16543439ed138dcb8d34, 0x78ad1b68d148c070372f8643c4648efbb63c6a8a338f3c24714868e791367653, 0xeba777d811cd36c06d540d7ff2ed18ed042fd67bbf7c9afcf88c818c7ee6b498, 0x0014a06d322ff07fcc02b12f93eb77bb76e28cdee4fc0670b9dec98d24bbfec8, 0x7b8a1d293670124924a0f532213753b89db10bde737249d4540e9a03657d1aff"
roleList = roleList.split(", ")
tx = Authorizer.grantRoles(roleList, BatchRelayer.address, {"from": daomsig})
tx.call_trace(expand=True)

a.reversebook["0x1802953277FD955f9a254B80Aa0582f193cF1d77"]
ProtocolFeesPercentagesProvider = Contract.from_explorer(
    "0x1802953277FD955f9a254B80Aa0582f193cF1d77"
)
roleList = "0xbe2a180d5cc5d803a8eec4cea569989fc1c593d7eeadd1f262f360a68b0e842e, 0xb28b769768735d011b267f781c3be90bce51d5059ba015bc7a28b3e882fb2083"
roleList = roleList.split(", ")
tx = Authorizer.grantRoles(
    roleList, ProtocolFeesPercentagesProvider.address, {"from": daomsig}
)
tx.call_trace(expand=True)


a.reversebook["0x230a59F4d9ADc147480f03B0D3fFfeCd56c3289a"]
ProtocolFeesWithdawer = Contract("0x230a59F4d9ADc147480f03B0D3fFfeCd56c3289a")
roleList = ["0xb2b6e48fa160a7c887d9d7a68b6a9bb9d47d4953d33e07f3a39e175d75e97796"]
tx = Authorizer.grantRoles(roleList, ProtocolFeesWithdawer.address, {"from": daomsig})
tx.call_trace(expand=True)

roleList = ["0xbeb10dd1f094c0751dc69e30b35c3f37cee8a9303f6e7380c83d31adcba39ea8"]
tx = Authorizer.grantRoles(roleList, daomsig, {"from": daomsig})
tx.call_trace(expand=True)

### 303A
tx = ProtocolFeesPercentagesProvider.setFeeTypePercentage(
    0, 500000000000000000, {"from": daomsig}
)
tx.call_trace(expand=True)

tx = ProtocolFeesPercentagesProvider.setFeeTypePercentage(
    2, 500000000000000000, {"from": daomsig}
)
tx.call_trace(expand=True)

### 303B
roleList = ["0x28eae42992658aefe28d2ca017a285a62376e3196f2ea3207d6e25d2dd31822d"]
tx = Authorizer.grantRoles(roleList, daomsig, {"from": daomsig})
tx.call_trace(expand=True)

a.reversebook["0x475D18169BE8a89357A9ee3Ab00ca386d20fA229"]
L2BalancerPseudoMinter = Contract("0x475D18169BE8a89357A9ee3Ab00ca386d20fA229")
tx = L2BalancerPseudoMinter.addGaugeFactory(
    "0x2498A2B0d6462d2260EAC50aE1C3e03F4829BA95", {"from": daomsig}
)
tx.call_trace(expand=True)
tx = Authorizer.revokeRoles(roleList, daomsig, {"from": daomsig})
tx.call_trace(expand=True)

### 303C
roleList = ["0x1cbb503dcc0f4acaedf71a098211ff8b15a220fc26a6974a8d9deaab040fa6e0"]
tx = Authorizer.grantRoles(roleList, daomsig, {"from": daomsig})
tx.call_trace(expand=True)
vault = Contract("0xBA12222222228d8Ba445958a75a0704d566BF2C8")
tx = vault.setAuthorizer(
    "0x8df317a729fcaA260306d7de28888932cb579b88", {"from": daomsig}
)
tx.call_trace(expand=True)
tx = Authorizer.revokeRoles(roleList, daomsig, {"from": daomsig})
tx.call_trace(expand=True)
