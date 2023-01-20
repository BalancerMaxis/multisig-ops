// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.7.1;

interface IBALTokenHolder {
    function getActionId(bytes4 selector) external view returns (bytes32);

    function getAuthorizer() external view returns (address);

    function getBalancerToken() external view returns (address);

    function getName() external view returns (string memory);

    function getVault() external view returns (address);

    function sweepTokens(
        address token,
        address recipient,
        uint256 amount
    ) external;

    function withdrawFunds(address recipient, uint256 amount) external;
}
