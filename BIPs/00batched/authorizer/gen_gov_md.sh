#!/bin/bash
### This generates a governance MD from template based on the following environment variables


#BIP_NUMBER = The BIP number for the governance
#PR_NUMBER = The PR number for the governance
#TABLE_MD = An the path to a table to dump into the Specification section


sed "s/XXX/$BIP_NUMBER/g" governance_template.md > .working.md
sed "s/YYY/$PR_NUMBER/g" .working.md > .working1.md
sed "/ADDRESS_SORTED_MD_TABLE/r $TABLE_MD" .working1.md | sed 's/ADDRESS_SORTED_MD_TABLE//' > ${BIP_NUMBER}.md
rm .working*.md