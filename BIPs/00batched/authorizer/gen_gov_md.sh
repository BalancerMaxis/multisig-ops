#!/bin/bash
### This generates a governance MD from template based on the following environment variables


#BIP_NUMBER = The BIP number for the governance
#PR_NUMBER = The PR number for the governance
#date=$(date '+%Y-%m-%d')
if [ -z $DATE ]; then
  echo "No Date"
  exit 2
fi
if [ -z $BIP_NUMBER ]; then
  echo "No BIP NUMBER"
  exit 3
fi
if [ -z $PR_NUMBER ]; then
  echo "No PR NUMBER"
  exit 4
fi
if [ -z $WEEKLY_DIR ]; then
  echo "No Weekly DIR"
  exit 5
fi

BIP_DIR="../../$WEEKLY_DIR/BIP-$BIP_NUMBER"
BIP_DIR_FROM_REPO_ROOT="BIPS/$WEEKLY_DIR/BIP-$BIP_NUMBER"

date=$DATE
## Setup git
git config --global user.name "BIP Bot"
git config --global user.email "bipbot@nowhere.gov"

echo "Creating $BIP_DIR and moving generated files into place."
mkdir -p $BIP_DIR
mv ${date}.json ${BIP_DIR}/inputs.json
mv ${date}_address_sorted.md ${BIP_DIR}/results_address_sorted.md
mv ${date}_deployment_sorted.md ${BIP_DIR}/results_deployment_sorted.md
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
sed "s/{BIP_NUMBER}/$BIP_NUMBER/g" governance_template.md > .working.md
sed "s/{PR_NUMBER}/$PR_NUMBER/g" .working.md > .working1.md
sed "s'{BIP_DIR}'$BIP_DIR_FROM_REPO_ROOT'g" .working1.md > .working2.md
sed "/ADDRESS_SORTED_MD_TABLE/r $TABLE" .working2.md | sed 's/ADDRESS_SORTED_MD_TABLE//' > ${BIP_DIR}/BIP-${BIP_NUMBER}.md
echo "[See Here](BIP-${BIP_NUMBER}.md) for the governance contents." > ${BIP_DIR}/README.md

rm .working*.md

git pull
git add -A
git add -u # find moved files
git commit -m "Setting up Payload Directory."
git push origin
BRANCH=`git branch --show-current`
git checkout staging
git merge $BRANCH
git push origin
git checkout $BRANCH
