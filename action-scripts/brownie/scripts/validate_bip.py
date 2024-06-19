import os
from typing import Tuple

from .script_utils import get_changed_files, extract_bip_number
from bal_addresses import AddrBook
from bal_addresses import to_checksum_address
from prettytable import MARKDOWN, PrettyTable
import re
import web3

ADDRESSES_MAINNET = AddrBook("mainnet").reversebook
ADDRESSES_POLYGON = AddrBook("polygon").reversebook
ADDRESSES_ARBITRUM = AddrBook("arbitrum").reversebook
ADDRESSES_AVALANCHE = AddrBook("avalanche").reversebook
ADDRESSES_OPTIMISM = AddrBook("optimism").reversebook
ADDRESSES_GNOSIS = AddrBook("gnosis").reversebook
ADDRESSES_ZKEVM = AddrBook("zkevm").reversebook
ADDRESSES_BASE = AddrBook("base").reversebook
ADDRESSES_FANTOM = AddrBook("fantom").reversebook
# Merge all addresses into one dictionary
ADDRESSES = {
    **ADDRESSES_MAINNET,
    **ADDRESSES_POLYGON,
    **ADDRESSES_ARBITRUM,
    **ADDRESSES_AVALANCHE,
    **ADDRESSES_OPTIMISM,
    **ADDRESSES_GNOSIS,
    **ADDRESSES_ZKEVM,
    **ADDRESSES_BASE,
    **ADDRESSES_FANTOM,
}


def validate_contains_msig(file: dict) -> Tuple[bool, str]:
    """
    Validates that file contains a multisig transaction
    """
    msig = file["meta"].get("createdFromSafeAddress") or file["meta"].get(
        "createFromSafeAddress"
    )
    if not msig or not isinstance(msig, str):
        return False, "No msig address found or it is not a string"
    return True, ""


def validate_msig_in_address_book(file: dict) -> Tuple[bool, str]:
    """
    Validates that multisig address is in address book
    """
    msig = file["meta"].get("createdFromSafeAddress") or file["meta"].get(
        "createFromSafeAddress"
    )
    if to_checksum_address(msig) not in ADDRESSES:
        return False, "Multisig address not found in address book"
    return True, ""


def validate_chain_specified(file: dict) -> Tuple[bool, str]:
    """
    Validates that chain is specified in file
    """
    chain = file.get("chainId")
    chains = list(AddrBook.chain_ids_by_name.values())
    if int(chain) not in chains:
        return (
            False,
            f"No chain specified or is not found in known chain list: {chain} in {chains}",
        )
    return True, ""


def validate_file_has_bip(file: dict) -> Tuple[bool, str]:
    """
    Validates that a single BIP number can be determined from the file path
    """
    bip = extract_bip_number(file)
    if bip == "N/A":
        return False, f"No BIP number found in file path {file['file_name']}"
    return True, ""


def validate_path_has_weekly_dir(file: dict) -> Tuple[bool, str]:
    """
    Validates that a files are in weekly directories can be determined from the file path
    """
    filename = file["file_name"]
    match = re.search(r"(\d{4})-W(\d{1,2})", filename)
    if not match:
        return False, f"File {filename} has has no YYYY-W## in path"
    return True, ""


# Add more validators here as needed
VALIDATORS = [
    validate_contains_msig,
    validate_msig_in_address_book,
    validate_chain_specified,
    validate_file_has_bip,
    validate_path_has_weekly_dir,
]


def main() -> None:
    files = get_changed_files()
    # Filter out merged jsons that are placed under 00batched folder
    files = [file for file in files if "00batched" not in file["file_name"]]
    # Run each file through validators and collect output in form of a dictionary
    results = {}
    for file in files:
        file_path = file["file_name"]
        results[file_path] = {}
        for validator in VALIDATORS:
            is_valid, output_msg = validator(file)
            if not is_valid:
                results[file_path][validator.__name__] = output_msg
            else:
                results[file_path][validator.__name__] = "OK"

    # Generate report for each file and save it in a list
    reports = []
    for file_path, file_results in results.items():
        report = f"BIP validation results for file `{file_path}`:\n"
        # Commit:
        report += f"Commit: `{os.getenv('COMMIT_SHA')}`\n"
        # Convert output for each file into table format
        table = PrettyTable(align="l")
        table.set_style(MARKDOWN)
        table.field_names = ["Validator", "Result"]
        table.align["Result"] = "c"
        for validator_name, result in file_results.items():
            table.add_row([f"`{validator_name}`", result])
        report += table.get_string()
        reports.append(report)

    # Save temporary file with results so that it can be used in github action later
    if reports:
        with open("validate_bip_results.txt", "w") as f:
            f.write("\n\n".join(reports))


if __name__ == "__main__":
    main()
