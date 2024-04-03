import requests
from datetime import datetime, timedelta
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Delete GitHub workflow runs older than a specified number of days.')
parser.add_argument('repo_owner', help='Repository owner')
parser.add_argument('repo_name', help='Repository name')
parser.add_argument('-t', '--github_token', required=True, help='GitHub Personal Access Token')
parser.add_argument('-d', '--retention_days', type=int, default=30, help='Retention period in days (default is 30 days)')

# Parse arguments
args = parser.parse_args()

# Constants from arguments
GITHUB_TOKEN = args.github_token
REPO_NAME = args.repo_name
REPO_OWNER = args.repo_owner
RETENTION_DAYS = args.retention_days
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"

# Headers
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_TOKEN}"
}

# Calculate the cutoff date based on retention period
cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)

# Get the list of workflow runs
print(f"Retrieving workflow runs for repository {REPO_OWNER}/{REPO_NAME}.", end='', flush=True)
list_runs_url = f"{BASE_URL}?per_page=100"
workflow_runs = []
while list_runs_url:
    response = requests.get(list_runs_url, headers=headers)
    if response.status_code != 200:
        print(f"[FAIL]\nError: {response.text}")
        exit(1)
    else:
        print(".", end='', flush=True)
        data = response.json()
        workflow_runs.extend(data.get('workflow_runs', []))
        
        # Parsing the Link header to find the URL for the next page
        link_header = response.headers.get('Link')
        next_page = None
        if link_header:
            links = link_header.split(', ')
            for link in links:
                if 'rel="next"' in link:
                    next_page = link[link.find("<") + 1:link.find(">")]

        list_runs_url = next_page

print(f"[OK]\nRetrieved {len(workflow_runs)} workflow runs.")

# Filter out workflow runs that are within the retention period
workflow_runs_to_delete = []
for run in workflow_runs:
    created_at = datetime.strptime(run['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    if created_at < cutoff_date:
        workflow_runs_to_delete.append(run)

print(f"{len(workflow_runs_to_delete)} are older than {cutoff_date} and eligible for deletion.")

# Ask for user confirmation before deleting, ensuring valid input
while True:
    user_confirmation = input(f"Continue expired deleting runs? (yes/no): ").strip().lower()
    if user_confirmation in ['yes', 'y']:
        break
    elif user_confirmation in ['no', 'n']:
        print("Deletion cancelled by the user.")
        exit(0)
    else:
        print("Please type 'yes' or 'no'.")

# Iterate through the workflow runs
count = 0
total = len(workflow_runs_to_delete)
for run in workflow_runs_to_delete:
    count+=1
    run_id = run['id']
    created_at = datetime.strptime(run['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    
    # Check if the run is older than the retention period
    if created_at >= cutoff_date:
        print(f"Workflow run {run_id} is within the retention period and was not deleted.")
        continue

    print(f"Deleting workflow {count} of {total}, run {run_id}...", end='')
    delete_url = f"{BASE_URL}/{run_id}"
    delete_response = requests.delete(delete_url, headers=headers)
    
    if delete_response.status_code == 204:
        print("[OK]")
    else:
        print("[FAIL]")
        print(f"Error: {delete_response.text}")
