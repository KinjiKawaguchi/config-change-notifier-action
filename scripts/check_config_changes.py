import os
import yaml
import sys
import requests
from typing import List

def get_config_files() -> List[str]:
    config_files_str = os.environ.get('CONFIG_FILES', '')
    return [file.strip() for file in config_files_str.split('\n') if file.strip()]

def check_file_changes(file_path: str) -> bool:
    diff_output = os.popen(f'git diff origin/main..HEAD -- {file_path}').read()
    return bool(diff_output.strip())

def add_pr_comment(comment: str):
    pr_number = os.environ.get('PR_NUMBER')
    token = os.environ.get('GITHUB_TOKEN')
    if not pr_number or not token:
        print("PR number or GitHub token is not set.")
        return

    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 201:
        print(f"Failed to add PR comment: {response.text}")

def main():
    config_files = get_config_files()
    changed_files = [file for file in config_files if check_file_changes(file)]

    if changed_files:
        print("The following config files have been changed:")
        for file in changed_files:
            print(f"- {file}")
        
        comment = (
            "Changes detected in the following config files:\n" +
            "\n".join(f"- {file}" for file in changed_files) + "\n\n" +
            "Please ensure these changes have been shared with the team.\n"
            "After confirming, please comment `/config-change-notified` on this PR."
        )
        add_pr_comment(comment)
        
        sys.exit(1)
    else:
        print("No changes detected in config files.")

if __name__ == "__main__":
    main()
