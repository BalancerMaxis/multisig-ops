#!/usr/bin/env python3
"""
Test the parse_contract_input function in isolation
"""

import pytest
import sys
import os

# Add parent directory to path to import script_utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.script_utils import parse_contract_input


def test_parse_simple_arrays():
    """Test parsing of simple array types"""
    # Test address array
    users_input = "[0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e]"
    users_result = parse_contract_input(users_input, "address[]")
    assert len(users_result) == 1
    assert users_result[0] == "0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e"

    # Test another address array
    tokens_input = "[0x513c7E3a9c69cA3e22550eF58AC1C0088e918FFf]"
    tokens_result = parse_contract_input(tokens_input, "address[]")
    assert len(tokens_result) == 1
    assert tokens_result[0] == "0x513c7E3a9c69cA3e22550eF58AC1C0088e918FFf"

    # Test uint256 array
    amounts_input = "[1591419645561974052491]"
    amounts_result = parse_contract_input(amounts_input, "uint256[]")
    assert len(amounts_result) == 1
    assert amounts_result[0] == 1591419645561974052491


def test_parse_multi_dimensional_arrays():
    """Test parsing of multi-dimensional arrays like bytes32[][]"""
    # Test the problematic bytes32[][] from merkl payload
    proofs_input = "[[0xe319fcfb3b29dc4e973abbb972a09ec46da5cc2d4afb08ac24968cccc950531d,0xcc81ec145221d28c079bfde3b7118bc092f3814f634228c720913a684b79bbc0,0x984581d1d45139d687b6e782029c74c7e6f368ad882f456107449e220fd12f74,0x0b13b4262816286e1a15a1d1af7df6481d174d2d82883a4b58d7369a71c34f45,0x3f7fba2701c31890b637ed2fe195d5ccab57068180d32683e091a5cdaee92c9a,0xcc3671dc3c70b19f8a9b1b990144e4d3c448f82dd5b5691880fe9f012388ff08,0x7081263404469b92c185a3118a4d2bd3d4529ba1e6b28b2d0f1c62514e5d6031,0xa32e1ed00800b1998b7f109908c6b29d57bf693c90b46b50793802c072f65e8e,0xbab26d7b083146587e71a81068d5d3847a68a09422547fc7b09d59526e4beff7,0x326a9bfc3facf9407ce61f3d84693b5ee1251ff8dce8f16a7953cebb9608680e,0x3f02e6a74270c95ec72225276e970f4c14be4bae25f0e0ed7819dad5a6ba92b7,0x2e858debb1d3b00e4df924769c590c14fb2b8b270d4e3238245eec444f274a0b,0x1485f84e5448ed5ce808e3b269ca413e077d8a1797b0b23948ad06b584f9b977,0xef5961e78fe0678b66833a5fc1634d7835341c98c40c4fe1295557bfc3500cf4]]"

    proofs_result = parse_contract_input(proofs_input, "bytes32[][]")

    assert len(proofs_result) == 1
    assert len(proofs_result[0]) == 14
    assert (
        proofs_result[0][0]
        == "0xe319fcfb3b29dc4e973abbb972a09ec46da5cc2d4afb08ac24968cccc950531d"
    )
    assert (
        proofs_result[0][-1]
        == "0xef5961e78fe0678b66833a5fc1634d7835341c98c40c4fe1295557bfc3500cf4"
    )


def test_parse_primitive_types():
    """Test parsing of primitive types"""
    # Test bool
    assert parse_contract_input("true", "bool") == True
    assert parse_contract_input("false", "bool") == False

    # Test uint256
    assert parse_contract_input("12345", "uint256") == 12345
    assert parse_contract_input("0", "uint256") == 0

    # Test address
    addr = "0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e"
    assert parse_contract_input(addr, "address") == addr

    # Test bytes32
    bytes32_val = "0xe319fcfb3b29dc4e973abbb972a09ec46da5cc2d4afb08ac24968cccc950531d"
    assert parse_contract_input(bytes32_val, "bytes32") == bytes32_val


def test_parse_already_parsed_values():
    """Test that already parsed values are returned as-is"""
    # Already parsed list
    parsed_list = ["0x123", "0x456"]
    assert parse_contract_input(parsed_list, "address[]") == parsed_list

    # Already parsed int
    assert parse_contract_input(12345, "uint256") == 12345

    # Already parsed bool
    assert parse_contract_input(True, "bool") == True


def test_parse_multiple_arrays():
    """Test parsing of multiple arrays in bytes32[][]"""
    # Test with multiple proof arrays
    multi_proofs = "[[0x123,0x456],[0x789,0xabc]]"
    result = parse_contract_input(multi_proofs, "bytes32[][]")

    assert len(result) == 2
    assert len(result[0]) == 2
    assert len(result[1]) == 2
    assert result[0][0] == "0x123"
    assert result[1][1] == "0xabc"


def test_parse_empty_arrays():
    """Test parsing of empty arrays"""
    # Empty single array
    assert parse_contract_input("[]", "address[]") == []

    # Empty nested array
    assert parse_contract_input("[[]]", "bytes32[][]") == [[]]


def test_parse_mixed_arrays():
    """Test parsing arrays with different types"""
    # Bool array
    bool_array = "[true,false,true]"
    result = parse_contract_input(bool_array, "bool[]")
    assert result == [True, False, True]

    # Mixed case bool
    mixed_bool = "[True,FALSE,true]"
    result = parse_contract_input(mixed_bool, "bool[]")
    assert result == [True, False, True]
