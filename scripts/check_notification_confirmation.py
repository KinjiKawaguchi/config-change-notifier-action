import os
import requests
import sys

def check_notification_confirmation():
    pr_number = os.environ.get('PR_NUMBER')
    token = os.environ.get('GITHUB_TOKEN')
    if not pr_number or not token:
        print("PR number or GitHub token is not set.")
        return False

    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch PR comments: {response.text}")
        return False

    comments = response.json()
    return any("/config-change-notified" in comment['body'] for comment in comments)

def main():
    if check_notification_confirmation():
        print("Notification confirmation command has been executed.")
    else:
        print("Notification confirmation command has not been executed. Please comment '/config-change-notified' on the PR.")
        sys.exit(1)

if __name__ == "__main__":
    main()
