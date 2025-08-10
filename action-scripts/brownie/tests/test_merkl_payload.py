#!/usr/bin/env python3
"""
Test script to verify the fix for parsing complex contract inputs in merkl payloads.
Tests the epoch_3-merit-43114.json payload that was causing Web3ValidationError.
"""

import json
import os
import sys
import pytest

# Add the action-scripts path to import script_utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.script_utils import parse_contract_input


def test_merkl_payload_parsing():
    """Test parsing the actual merkl payload that was causing errors"""

    # Get the path to the payload file
    repo_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    )
    payload_path = os.path.join(
        repo_root, "MaxiOps/merkl/payloads/epoch_3-merit-43114.json"
    )

    # Check if file exists
    if not os.path.exists(payload_path):
        pytest.skip(f"Payload file not found at {payload_path}")

    with open(payload_path, "r") as f:
        payload = json.load(f)

    # Test the first transaction (the problematic claim function)
    tx = payload["transactions"][0]

    # Verify transaction structure
    assert tx["to"] == "0x3Ef3D8bA38EBe18DB133cEc108f4D14CE00Dd9Ae"
    assert tx["contractMethod"]["name"] == "claim"

    # Process each input
    processed_inputs = {}
    for input_spec in tx["contractMethod"]["inputs"]:
        param_name = input_spec["name"]
        param_type = input_spec["type"]
        param_value = tx["contractInputsValues"][param_name]

        # This should not raise an error
        processed_value = parse_contract_input(param_value, param_type)
        processed_inputs[param_name] = processed_value

    # Verify the processed values
    assert "users" in processed_inputs
    assert "tokens" in processed_inputs
    assert "amounts" in processed_inputs
    assert "proofs" in processed_inputs

    # Check users array
    assert isinstance(processed_inputs["users"], list)
    assert len(processed_inputs["users"]) == 1
    assert processed_inputs["users"][0] == "0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e"

    # Check tokens array
    assert isinstance(processed_inputs["tokens"], list)
    assert len(processed_inputs["tokens"]) == 1
    assert processed_inputs["tokens"][0] == "0x513c7E3a9c69cA3e22550eF58AC1C0088e918FFf"

    # Check amounts array
    assert isinstance(processed_inputs["amounts"], list)
    assert len(processed_inputs["amounts"]) == 1
    assert processed_inputs["amounts"][0] == 1591419645561974052491

    # Check proofs array (bytes32[][])
    assert isinstance(processed_inputs["proofs"], list)
    assert len(processed_inputs["proofs"]) == 1
    assert isinstance(processed_inputs["proofs"][0], list)
    assert len(processed_inputs["proofs"][0]) == 14

    # Verify first and last proof elements
    assert (
        processed_inputs["proofs"][0][0]
        == "0xe319fcfb3b29dc4e973abbb972a09ec46da5cc2d4afb08ac24968cccc950531d"
    )
    assert (
        processed_inputs["proofs"][0][-1]
        == "0xef5961e78fe0678b66833a5fc1634d7835341c98c40c4fe1295557bfc3500cf4"
    )


def test_all_merkl_transactions():
    """Test parsing all transactions in the merkl payload"""

    # Get the path to the payload file
    repo_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    )
    payload_path = os.path.join(
        repo_root, "MaxiOps/merkl/payloads/epoch_3-merit-43114.json"
    )

    # Check if file exists
    if not os.path.exists(payload_path):
        pytest.skip(f"Payload file not found at {payload_path}")

    with open(payload_path, "r") as f:
        payload = json.load(f)

    # Process all transactions
    for idx, tx in enumerate(payload["transactions"]):
        if "contractMethod" in tx and tx["contractMethod"] is not None:
            # Process each input
            for input_spec in tx["contractMethod"]["inputs"]:
                param_name = input_spec["name"]
                param_type = input_spec["type"]

                # Skip if contractInputsValues is None
                if tx.get("contractInputsValues") is None:
                    continue

                param_value = tx["contractInputsValues"].get(param_name)
                if param_value is not None:
                    # This should not raise an error
                    processed_value = parse_contract_input(param_value, param_type)

                    # Basic type checks
                    if "[]" in param_type:
                        assert isinstance(
                            processed_value, list
                        ), f"Transaction {idx}: Expected list for {param_name}"
                    elif param_type == "bool":
                        assert isinstance(
                            processed_value, bool
                        ), f"Transaction {idx}: Expected bool for {param_name}"
                    elif "int" in param_type:
                        assert isinstance(
                            processed_value, int
                        ), f"Transaction {idx}: Expected int for {param_name}"
                    elif param_type == "address":
                        assert isinstance(
                            processed_value, str
                        ), f"Transaction {idx}: Expected string for {param_name}"
                        assert processed_value.startswith(
                            "0x"
                        ), f"Transaction {idx}: Address should start with 0x"


def test_tuple_parsing():
    """Test parsing of tuple parameters from the merkl payload"""

    # Get the path to the payload file
    repo_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    )
    payload_path = os.path.join(
        repo_root, "MaxiOps/merkl/payloads/epoch_3-merit-43114.json"
    )

    # Check if file exists
    if not os.path.exists(payload_path):
        pytest.skip(f"Payload file not found at {payload_path}")

    with open(payload_path, "r") as f:
        payload = json.load(f)

    # Find a transaction with tuple input (createCampaign)
    for tx in payload["transactions"]:
        if tx.get("contractMethod", {}).get("name") == "createCampaign":
            input_spec = tx["contractMethod"]["inputs"][0]
            assert input_spec["type"] == "tuple"
            assert input_spec["name"] == "newCampaign"

            # Get the tuple value
            tuple_value = tx["contractInputsValues"]["newCampaign"]
            components = input_spec["components"]

            # Parse the tuple
            parsed_tuple = parse_contract_input(tuple_value, "tuple", components)

            # Verify it's a tuple
            assert isinstance(parsed_tuple, tuple)
            assert len(parsed_tuple) == len(components)

            # Check some specific values
            # campaignId (bytes32) - should be the zero hash
            assert (
                parsed_tuple[0]
                == "0x0000000000000000000000000000000000000000000000000000000000000000"
            )
            # creator (address) - should be zero address
            assert parsed_tuple[1] == "0x0000000000000000000000000000000000000000"
            # rewardToken (address)
            assert parsed_tuple[2] == "0x513c7E3a9c69cA3e22550eF58AC1C0088e918FFf"
            # amount (uint256) - should be an integer
            assert isinstance(parsed_tuple[3], int)

            break
