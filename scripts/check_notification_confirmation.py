import os
import requests
import sys
import time

def get_localized_messages():
    language = os.environ.get('LANGUAGE', 'en')
    messages = {
        'en': {
            'executed': "Notification confirmation command has been executed.",
            'waiting': "Waiting for the notification confirmation command. Please comment '/config-change-notified' on the PR when ready.",
            'error': "PR number or GitHub token is not set."
        },
        'ja': {
            'executed': "通知確認コマンドが実行されました。",
            'waiting': "通知確認コマンドを待っています。準備ができたらPRに '/config-change-notified' とコメントしてください。",
            'error': "PR番号またはGitHubトークンが設定されていません。"
        }
    }
    return messages.get(language, messages['en'])
    
def check_notification_confirmation():
    pr_number = os.environ.get('PR_NUMBER')
    token = os.environ.get('GITHUB_TOKEN')
    messages = get_localized_messages()
    
    if not pr_number or not token:
        print(messages['error'])
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
    return any(comment['body'].strip() == "/config-change-notified" for comment in comments)

def wait_for_notification_confirmation():
    messages = get_localized_messages()
    check_interval = 5  # 1分ごとにチェック

    print(messages['waiting'])
    while True:
        if check_notification_confirmation():
            print(messages['executed'])
            return True
        time.sleep(check_interval)

def main():
    wait_for_notification_confirmation()

if __name__ == "__main__":
    main()