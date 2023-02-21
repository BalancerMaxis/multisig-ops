//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract testToken is ERC20{
    constructor (address _founder, uint256 _initialSupply) ERC20("TestToken","ShortTEST"){
        _mint(_founder,_initialSupply);
    }
}