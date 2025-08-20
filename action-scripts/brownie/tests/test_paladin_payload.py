#!/usr/bin/env python3
"""
Test script to verify the fix for parsing paladin bribe payloads.
"""

import sys
import os

# Add parent directory to path to import script_utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.script_utils import parse_contract_input


def test_paladin_merkle_proof_parsing():
    """Test parsing of merkleProof from paladin bribe payload"""

    # Test the problematic merkleProof formats from paladin payload
    test_cases = [
        # Python-style list with single quotes
        (
            "['0xea1452517ef03ca99824d4d9fe0a5dc56a205798e139865c9265ec2336b2cbad', '0x85401f3a6bcd63632f2b78998ed8e64f6bce505bb32f250c00fa28a8d1a1729d']",
            "bytes32[]",
            [
                "0xea1452517ef03ca99824d4d9fe0a5dc56a205798e139865c9265ec2336b2cbad",
                "0x85401f3a6bcd63632f2b78998ed8e64f6bce505bb32f250c00fa28a8d1a1729d",
            ],
        ),
        # Single element
        (
            "['0x15ac28f8f31929bb73cbc8103ca7775ee2d2115441bf25902394ed2fffd1aeb8']",
            "bytes32[]",
            ["0x15ac28f8f31929bb73cbc8103ca7775ee2d2115441bf25902394ed2fffd1aeb8"],
        ),
        # Three elements
        (
            "['0x218324e500df97b997ef1b68e4c91d5eeedd8c000c4c86b767226c8eb0f9b37f', '0x4fb0139b23a71b710a0d4c2204888e111a3965eb7e628d117015ecbc0803df2e', '0xdebebbc06cfbbbd72ca2a75d4ab72796fa469e5d3dbc6317cdc238908a5b73f3']",
            "bytes32[]",
            [
                "0x218324e500df97b997ef1b68e4c91d5eeedd8c000c4c86b767226c8eb0f9b37f",
                "0x4fb0139b23a71b710a0d4c2204888e111a3965eb7e628d117015ecbc0803df2e",
                "0xdebebbc06cfbbbd72ca2a75d4ab72796fa469e5d3dbc6317cdc238908a5b73f3",
            ],
        ),
        # Four elements
        (
            "['0x747f684f4062d51ce575b534ae7a61f71a0cbd3990c3231c757a44971ca1796a', '0x39ad809022c40cd60c8c04ad58a2e5aa65ab27901ca9a1633cb8fb44931fddaf', '0x37e276532fc287c37671390ed789dc1a119a1779f5f6265561a2a0b6a43de38c', '0xf4bf6c8b33807d1400e672ab643614f90432e83ba91bcbd1fac963b62427cb7b']",
            "bytes32[]",
            [
                "0x747f684f4062d51ce575b534ae7a61f71a0cbd3990c3231c757a44971ca1796a",
                "0x39ad809022c40cd60c8c04ad58a2e5aa65ab27901ca9a1633cb8fb44931fddaf",
                "0x37e276532fc287c37671390ed789dc1a119a1779f5f6265561a2a0b6a43de38c",
                "0xf4bf6c8b33807d1400e672ab643614f90432e83ba91bcbd1fac963b62427cb7b",
            ],
        ),
    ]

    for value, param_type, expected in test_cases:
        result = parse_contract_input(value, param_type)
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) == len(
            expected
        ), f"Expected {len(expected)} elements, got {len(result)}"
        assert result == expected, f"Values don't match: {result} != {expected}"


def test_paladin_payload_full():
    """Test parsing a full transaction from paladin payload"""

    # Simulate processing of a paladin claim transaction
    contract_inputs = {
        "questID": "223",
        "period": "1744848000",
        "index": "0",
        "account": "0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e",
        "amount": "259262548911166789081",
        "merkleProof": "['0xea1452517ef03ca99824d4d9fe0a5dc56a205798e139865c9265ec2336b2cbad', '0x85401f3a6bcd63632f2b78998ed8e64f6bce505bb32f250c00fa28a8d1a1729d']",
    }

    input_types = {
        "questID": "uint256",
        "period": "uint256",
        "index": "uint256",
        "account": "address",
        "amount": "uint256",
        "merkleProof": "bytes32[]",
    }

    # Parse each input
    parsed_inputs = {}
    for param_name, param_value in contract_inputs.items():
        param_type = input_types[param_name]
        parsed_inputs[param_name] = parse_contract_input(param_value, param_type)

    # Verify the parsed values
    assert parsed_inputs["questID"] == 223
    assert parsed_inputs["period"] == 1744848000
    assert parsed_inputs["index"] == 0
    assert parsed_inputs["account"] == "0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e"
    assert parsed_inputs["amount"] == 259262548911166789081
    assert isinstance(parsed_inputs["merkleProof"], list)
    assert len(parsed_inputs["merkleProof"]) == 2
    assert (
        parsed_inputs["merkleProof"][0]
        == "0xea1452517ef03ca99824d4d9fe0a5dc56a205798e139865c9265ec2336b2cbad"
    )


def test_edge_cases():
    """Test edge cases for array parsing"""

    # Empty array with quotes
    assert parse_contract_input("[]", "bytes32[]") == []

    # Array with extra spaces
    assert parse_contract_input("[ '0x123' , '0x456' ]", "bytes32[]") == [
        "0x123",
        "0x456",
    ]

    # Double quotes instead of single
    result = parse_contract_input('["0x123", "0x456"]', "bytes32[]")
    assert result == ["0x123", "0x456"]

    # Mixed quotes (should still work with ast.literal_eval)
    result = parse_contract_input("['0x123', \"0x456\"]", "bytes32[]")
    assert result == ["0x123", "0x456"]


if __name__ == "__main__":
    print("Testing paladin payload parsing...")
    print("=" * 60)

    try:
        test_paladin_merkle_proof_parsing()
        print("✓ test_paladin_merkle_proof_parsing passed")
    except AssertionError as e:
        print(f"✗ test_paladin_merkle_proof_parsing failed: {e}")
        raise

    try:
        test_paladin_payload_full()
        print("✓ test_paladin_payload_full passed")
    except AssertionError as e:
        print(f"✗ test_paladin_payload_full failed: {e}")
        raise

    try:
        test_edge_cases()
        print("✓ test_edge_cases passed")
    except AssertionError as e:
        print(f"✗ test_edge_cases failed: {e}")
        raise

    print("\n✓ All tests passed!")
    print("The paladin payload parsing should now work correctly.")
