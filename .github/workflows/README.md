# README

## GitHub Actions: Environments

The `run_reports_reusable.yaml` workflow currently defines an explicit environment for the `generate_reports` job to run in via `environment:`. This is because in some places it is triggered via `pull_request_target`, which is different from the regular `pull_request` trigger in that it runs in the base (target) of the pr, and not the head. Quoted from this GitHub blog that introduced it:

> In order to protect public repositories for malicious users we run all pull request workflows raised from repository forks with a read-only token and no access to secrets. This makes common workflows like labeling or commenting on pull requests very difficult.
>
> In order to solve this, we’ve added a new pull_request_target event, which behaves in an almost identical way to the pull_request event with the same set of filters and payload. However, instead of running against the workflow and code from the merge commit, the event runs against the workflow and code from the base of the pull request. This means the workflow is running from a trusted source and is given access to a read/write token as well as secrets enabling the maintainer to safely comment on or label a pull request.

NOTE THE SECURITY RISK OF ANY USER BEING ABLE TO ACCESS SECRETS VIA A PR!!!

For this reason, forked prs run in the environment `"external"`, which has some protection rules set up.

DO NOT APPROVE DEPLOYMENTS IN THIS ENVIRONMENT WITHOUT CHECKING FOR MALICIOUS CODE!!!

DO NOT REMOVE THE ENVIRONMENTS PROTECTION RULES!!!
