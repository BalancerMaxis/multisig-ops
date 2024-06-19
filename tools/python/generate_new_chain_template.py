from bal_addresses import AddrBook
import json

a = AddrBook("mainnet")  # we don't care about addresses


def lookup_caller(caller):
    print(caller)
    if "/" in caller:
        print(f"caller: {caller} looks like it already is in flatbook format, skipping")
        return caller
    try:
        return a.search_unique(caller)
    except AddrBook.MultipleMatchesError as error:
        return a.reversebook[a.latest_contract(caller)]
    ## If we haven't returned yet no match was found
    raise AddrBook.NoResultsError(f"no match for {caller} found")


with open("../../BIPs/00batched/authorizer/new-chain-pretemplate.json", "r") as f:
    pretemplate = json.load(f)
template = []
for block in pretemplate:
    for function, callers in block["function_caller_map"].items():
        flatcallers = []
        if isinstance(callers, str):  ## don't require singleton lists
            callers = [callers]
        for caller in callers:
            flatcallers.append(lookup_caller(caller))
        block["function_caller_map"][function] = flatcallers
    template.append(block)


with open("../../BIPs/00batched/authorizer/new-chain-template.json", "w") as f:
    json.dump(template, f, indent=2)
