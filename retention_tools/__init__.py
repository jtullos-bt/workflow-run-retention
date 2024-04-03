from typing import Optional
import requests
from datetime import datetime, timedelta


def get_workflow_runs(
    repo_owner: str, repo_name: str, github_token: str, console_output: bool = True
) -> list[dict]:
    """
    Retrieve workflow runs from a GitHub repository.

    Args:
        repo_owner (str): The owner of the GitHub repository.
        repo_name (str): The name of the GitHub repository.
        github_token (str): GitHub personal access token for authentication.
        console_output (bool, optional): Whether to print console output. Defaults to True.

    Returns:
        List[dict]: A list of dictionaries representing the retrieved workflow runs.
    """
    base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}",
    }
    list_runs_url = f"{base_url}?per_page=100"
    workflow_runs = []

    if console_output:
        print("Retrieving workflow runs...", end="", flush=True)

    while list_runs_url:
        response = requests.get(list_runs_url, headers=headers)
        if response.status_code != 200:
            if console_output:
                print(f"[FAIL]\nError: {response.text}")
            exit(1)
        else:
            if console_output:
                print(".", end="", flush=True)
            data = response.json()
            workflow_runs.extend(data.get("workflow_runs", []))
            next_page_url = response.links.get("next", {}).get("url")
            list_runs_url = next_page_url

    if console_output:
        print(f"[OK]\nRetrieved {len(workflow_runs)} workflow runs.")

    return workflow_runs


def filter_workflow_runs(
    workflow_runs: list[dict],
    cutoff_date: datetime,
    workflow_name: Optional[str] = None,
) -> list[dict]:
    """
    Filter workflow runs based on expiration date and optional workflow name.

    Args:
        workflow_runs (list[dict]): A list of dictionaries representing workflow runs.
        cutoff_date (datetime): The cutoff date for filtering expired workflow runs.
        workflow_name (Optional[str], optional): The name of the workflow to filter by. Defaults to None.

    Returns:
        list[dict]: A list of filtered workflow runs.
    """
    filtered_runs = []
    for run in workflow_runs:
        created_at = datetime.strptime(run["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        is_expired = created_at < cutoff_date - timedelta(days=1)
        name_matches = workflow_name is None or workflow_name == run["name"]

        if is_expired and name_matches:
            filtered_runs.append(run)

    return filtered_runs


def delete_workflow_runs(
    workflow_runs: list, github_token: str, console_output: bool = True
) -> bool:
    """
    Delete workflow runs from GitHub repository.

    Args:
        workflow_runs (list): List of workflow runs to be deleted.
        github_token (str): GitHub personal access token for authentication.
        console_output (bool, optional): Whether to print console output. Defaults to True.

    Returns:
        bool: True if all workflow runs are successfully deleted, False otherwise.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}",
    }
    count = 0
    total = len(workflow_runs)

    for run in workflow_runs:
        count += 1
        run_id = run["id"]

        if console_output:
            print(f"Deleting workflow {count} of {total}, run {run_id}...", end="")

        delete_response = requests.delete(run["url"], headers=headers)

        if delete_response.status_code == 204:
            if console_output:
                print("[OK]")
        else:
            if console_output:
                print("[FAIL]")
                print(f"Error: {delete_response.text}")
            return False

    return True


def confirm_action(
    prompt: str = "Continue? (yes/no): ",
    cancel_message: str = "Action cancelled by the user.",
    positive_input: str = "yes",
    negative_input: str = "no",
) -> bool:
    """
    Ask for user confirmation before proceeding with an action, ensuring valid input.

    Args:
        prompt (str): The message prompting the user for confirmation.
        cancel_message (str): The message to display when the action is cancelled by the user.
        positive_input (str): The string representing positive confirmation from the user.
        negative_input (str): The string representing negative confirmation from the user.

    Returns:
        bool: True if the user confirms the action, False otherwise.
    """
    while True:
        user_confirmation = input(prompt).strip().lower()
        if user_confirmation == positive_input.lower():
            return True
        elif user_confirmation == negative_input.lower():
            print(cancel_message)
            return False
        else:
            print(f"Please type '{positive_input}' or '{negative_input}'.")
