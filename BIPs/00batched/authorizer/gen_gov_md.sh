#!/bin/bash
### This generates a governance MD from template based on the following environment variables


#BIP_NUMBER = The BIP number for the governance
#PR_NUMBER = The PR number for the governance
date=$(date '+%Y-%m-%d')
BIP_DIR="../../BIP-$BIP_NUMBER"

echo "Creating $BIP_DIR and moving generated files into place."
mkdir $BIP_DIR
mv ${date}.json ${BIP_DIR}/inputs.json
mv ${date}_address_sorted.md ${BIP_DIR}/result_address_sorted.md
mv ${date}_deployment_sorted.md ${BIP_DIR}/result_deloyment_sorted.md
mv ${date}_function_descriptions.md ${BIP_DIR}/function_descriptions.md

## move chain jsons
mkdir chains
for file in ${date}_*.json; do
  mv $file `echo $file | sed s/${date}_/chains\\\//`
done
mv chains/* $BIP_DIR
rm -r chains

## Build basic governance MD

TABLE=${BIP_DIR}/results_address_sorted.md

echo "Building governance forum md file.  Note you will need to review and update the top sections to talk a bit about the change and it's reasons."
sed "s/XXX/$BIP_NUMBER/g" governance_template.md > .working.md
sed "s/YYY/$PR_NUMBER/g" .working.md > .working1.md
sed "/ADDRESS_SORTED_MD_TABLE/r $TABLE" .working1.md | sed 's/ADDRESS_SORTED_MD_TABLE//' > ${BIP_DIR}/${BIP_NUMBER}.md
rm .working*.md