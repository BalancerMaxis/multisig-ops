import pytest
from brownie import Token, accounts, IERC2

@pytest.fixture
def token():
    return accounts[0].deploy(IERC20, "Test Token", "TST", 18, 10000);

