from pathlib import Path
import glob
from scripts.get_gauge_mappings import gen_report, get_payload_list

debug = False




def main():
    all_bips = glob.glob("../../BIPs/**/*.json", recursive=True)
    runlist = []
    for file in all_bips:
        runlist.append(file.replace("../../", ""))
    #reports = gen_report(runlist)
    reports = gen_report(["BIPs/2023-W20/BIP-297.json"])
    #reports = gen_report(get_payload_list())
    ### Generate comment output
    with open("output.txt", "w") as f:
        for report in reports:
            f.write(report)
    ### Generate output files
    for report in reports:
        filename = Path(f"{report.splitlines()[0]}")
        filename = filename.with_suffix(".report.txt")
        with open(f"../../{filename}", "w") as f:
            f.write(report)


if __name__ == "__main__":
    main()