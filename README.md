# GitHub Workflow Runs Retention Tool

This tool allows you to delete GitHub workflow runs older than a specified number of days from a repository.

## Prerequisites

Before using this tool, ensure you have the following:

- Python 3.x installed on your system.
- A GitHub Personal Access Token with sufficient permissions. You can create one [here](https://github.com/settings/tokens/new). Make sure it has the `repo` scope.

## Usage

To use the tool, follow these steps:

1. Clone this repository or download the script directly.

2. Navigate to the directory containing the script.

3. Install required packages using requirements.txt in this repository:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the script using the following command:
   ```bash
   python delete_workflow_runs.py <repo_owner> <repo_name> -t <github_token> [-d <retention_days>]
   ```

   * Replace `<repo_owner>` and `<repo_name>` with the owner and name of the repository from which you want to delete workflow runs.
   * Replace `<github_token>` with your GitHub Personal Access Token.
   * Optionally, you can specify the retention period in days using the `-d` or `--retention_days` argument. By default, it's set to 30 days.

5. Follow the prompts to confirm the deletion of workflow runs.

## Example

Here's an example command to delete workflow runs older than 30 days from a repository:

```bash
python delete_workflow_runs.py myusername myrepository -t YOUR_GITHUB_TOKEN -d 30
```

## Disclaimer

Use this tool at your own risk. The author is not responsible for any data loss or damage caused by the misuse of this tool.
