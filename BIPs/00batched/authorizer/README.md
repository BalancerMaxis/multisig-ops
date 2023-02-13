## Generate Authorizor JSON files and write most of the governance

### To use this
- Copy [00_input_example.json](00_input_example.json) to a new file.  Fill out the scripts
  - For each map in the list, the script will generate permissions to give the target access to the functions specified in the deployments specified on all the chains specified.
- Name your file with `YYYY_MM_DD`.json with todays date like `2023-01-31.json` and put it in this authorizer folder.
- Create a new branch with your file and push it to github.
- Create a pull request and label it "Generate Authorizer".  This could be the PR for the BIP.
 - A script should run and create the all the input files
 - Set the following environment vars

```bash
BIP_NUMBER= 
PR_NUMBER=
```
Where BIP number is the number of the BIP like 175, nad PR number is the number of the payload PR for that BIP, like 57

 - Run ./gen_gov_md.sh
   - A BIP-XXX folder will be created in the [BIPs folder at the root of this repo](../../) that contains all the payloads and md files and a BIP-XXX.MD with governance text to link them all.

### Merge into the `staging` branch
We need to merge
### Edit your governance

You can edit the governance BIP in your IDE  or in the forum and tidy it up and add context.  In the end, you should either update the governance MD file in the BIP folder with the final contents of what is posted to forum or delete it to avoid confusion 
