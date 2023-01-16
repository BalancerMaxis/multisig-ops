# Adding a gauge while remove another in order to deal with replacement pools
In this case we have to call operations against 2 different multisigs.  
- The DAO multisig to kill the old gauge 
- The Gauge Manager to add the new one

Because we need more than 1 JSON file, we will create a PR which has them all in a directory.  Note that to do this you
will need to use github desktop or an IDE to create a multi file pull request

## Remove the old gauge
Go To: https://gnosis-safe.io/app/eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f/apps?appUrl=https://apps.gnosis-safe.io/tx-builder
- Set Address to `0x8F42aDBbA1B16EaAE3BB5754915E0D06059aDd75`
- Set Data Bytes to `0xab8f0945`
- Set Target to the address of the gauge you wish to remove
- Click Add Transaction
- Click Create Batch
- Simulate and verify on tenderly
- Download the JSON file naming it `mainnetDaoMultisig.json`
## Add the new Gauge
Go To: https://gnosis-safe.io/app/eth:0xc38c5f97B34E175FFd35407fc91a937300E33860/apps?appUrl=https://apps.gnosis-safe.io/tx-builder

- Set Address to 0x2fFB7B215Ae7F088eC2530C7aa8E1B24E398f26a
- Select `Add___Gauge` where ___ is the chain the gauge is being added for
- Enter the mainnet address of the Gauge (Not the Pool) being added
- Click `Add Transaction`
- ![](images/gaugeRequest.png)
- Click `Create Batch`
- Simulate and verify
- ![](images/simulate.png)
- Click the Download on the top right.
  - Name the saved file `mainnetGaugeMultisig.json`

## Creating the PR
**Note that you will not be able to upload and create the PR directly on the GITHUB app in this case.  The upload feature only allows you to create a PR for a single file going into a directory that already exists.  Completing this example will require using a 3rd party tool to create a branch and commit and push it to github.  Github Desktop, or any IDE should enable this.**

Here are instructions for how to create the commit/PR:

- Create a directory called BIP-XXX, where XXX is the BIP number, in the `/BIPs` directory.
- Copy the 2 json files generated above into this directory
- Create a new branch named BIP-XXX where XXX is your bip number
- Commit the 2 new files in their directory to this branch and create a pull request
- Use the exact heading of the Forum/Snapshot post as the Pull Request Title

The BIP-157.example folder here shows what the structure should look like.


