// SPDX-License-Identifier: MIT
pragma solidity 0.8.12;

interface IBribeMarket {
    function depositBribe(
        bytes32 _proposal,
        address _token,
        uint256 _amount,
        uint256 _maxTokensPerVote,
        uint256 _periods
    ) external;
}