# Tutorial for Submitting Bi-Weekly Aura Gauge Votes on Snapshot


## Steps to Submit Votes

### Step 1: Prepare Your Voting Data

1. **Create a CSV File**: Prepare a CSV file with your voting data. use the template [here](https://docs.google.com/spreadsheets/d/1w63dyNGi0IB_bXgGXQk2lwknnT5wxCUkKHVp5bHqlFc/edit?gid=0#gid=0). The "chain" and "label" columns are for reference. Only the "gauge address" and "Allocation %" columns are read in by the script.
2. Save to a `input.csv`.


### Step 2: PR the Votes

1. **Upload the CSV File**:
    - Navigate to the `input` directory for the current week and year. For example, for week 25 of 2024, the path would be: **`MaxiOps/vlaura_voting/2024/W25/input`**.
    - Go to the URL: `https://github.com/BalancerMaxis/multisig-ops/upload/main/MaxiOps/vlaura_voting/2024/W25/input`. (replace with current year/W##)
    - Drag and drop your CSV file into the upload area or click "choose your files" to select the file from your computer.
    - Add a commit message, for example, "Add voting data for 2024-W25".
    - Ensure you select the option to "Create a new branch for this commit and start a pull request".
    - Name the branch appropriately, for example, `voting-data-2024-W25`.
    - Click the "Propose changes" button.

2. **Create a Pull Request (PR)**:
    - You will be redirected to the "Open a pull request" page.
    - Click the "Create pull request" button and assign reviewer(s)

### Step 3: Run the GitHub Action Workflow

1. **Wait for Review**: Wait for the PR to be reviewed and merged

1. **Navigate to Actions**:
    - Go to the [Actions tab](https://github.com/BalancerMaxis/multisig-ops/actions) in the repository.

2. **Run the Workflow**:
    - Find the workflow named "Post vlAURA snapshot votes to voter multisig and send to the vote relayer".
    - Click on the workflow and then click the "Run workflow" button on the right side.
    - Enter the `week-string` in the format `YYYY-W##`, for example, `2024-W25`.
    - Click the "Run workflow" button to start the process. (This will create a Safe transaction on the [voting multisig](https://app.safe.global/transactions/history?safe=eth:0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e))

Once the the Safe transaction is signed and executed, votes will be posted on Snapshot
