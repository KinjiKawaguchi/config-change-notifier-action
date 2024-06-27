import os
import requests
import sys

def get_localized_messages():
    language = os.environ.get('LANGUAGE', 'en')
    messages = {
        'en': {
            'executed': "Notification confirmation command has been executed.",
            'not_executed': "Notification confirmation command has not been executed. Please comment '/config-change-notified' on the PR.",
            'error': "PR number or GitHub token is not set."
        },
        'ja': {
            'executed': "通知確認コマンドが実行されました。",
            'not_executed': "通知確認コマンドが実行されていません。PRに '/config-change-notified' とコメントしてください。",
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
    return any("/config-change-notified" in comment['body'] for comment in comments)

def main():
    messages = get_localized_messages()
    if check_notification_confirmation():
        print(messages['executed'])
    else:
        print(messages['not_executed'])
        sys.exit(1)

if __name__ == "__main__":
    main()