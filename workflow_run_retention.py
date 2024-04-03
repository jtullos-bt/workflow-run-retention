from retention_tools import *
import argparse

parser = argparse.ArgumentParser(
    description="Delete GitHub workflow runs older than a specified number of days."
)
parser.add_argument("repo_owner", help="Repository owner")
parser.add_argument("repo_name", help="Repository name")
parser.add_argument(
    "-t", "--github_token", required=True, help="GitHub Personal Access Token"
)
parser.add_argument(
    "-d",
    "--retention_days",
    type=int,
    default=30,
    help="Retention period in days (default is 30 days)",
)
args = parser.parse_args()

GITHUB_TOKEN = args.github_token
REPO_NAME = args.repo_name
REPO_OWNER = args.repo_owner
RETENTION_DAYS = args.retention_days

cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
workflow_runs = get_workflow_runs(
    REPO_OWNER, REPO_NAME, GITHUB_TOKEN, console_output=True
)
workflow_runs_to_delete = filter_workflow_runs(workflow_runs, cutoff_date)

print(
    f"{len(workflow_runs_to_delete)} are older than {cutoff_date} and eligible for deletion."
)

if not confirm_action("Do you want to delete these workflow runs? "):
    print("Workflow runs deletion cancelled.")
    exit(0)

# Iterate through the workflow runs
if delete_workflow_runs(workflow_runs_to_delete, GITHUB_TOKEN, console_output=True):
    print("All workflow runs deleted successfully.")
    exit(0)
else:
    exit(1)
