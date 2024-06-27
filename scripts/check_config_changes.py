import os
import yaml
import sys
import requests
from typing import List, Dict

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

def get_localized_messages() -> Dict[str, str]:
    language = os.environ.get('LANGUAGE', 'en')
    messages = {
        'en': {
            'changes_detected': "Changes detected in the following config files:",
            'ensure_shared': "Please ensure these changes have been shared with the team.",
            'confirm_comment': "After confirming, please comment `/config-change-notified` on this PR.",
            'no_changes': "No changes detected in config files."
        },
        'ja': {
            'changes_detected': "以下の設定ファイルに変更が検出されました：",
            'ensure_shared': "これらの変更がチームと共有されていることを確認してください。",
            'confirm_comment': "確認後、このPRに `/config-change-notified` とコメントしてください。",
            'no_changes': "設定ファイルに変更は検出されませんでした。"
        }
    }
    return messages.get(language, messages['en'])
    
def main():
    config_files = get_config_files()
    changed_files = [file for file in config_files if check_file_changes(file)]
    messages = get_localized_messages()
    
    if changed_files:
        print(messages['changes_detected'])
        for file in changed_files:
            print(f"- {file}")
        
        comment = (
            f"{messages['changes_detected']}\n" +
            "\n".join(f"- {file}" for file in changed_files) + "\n\n" +
            f"{messages['ensure_shared']}\n" +
            f"{messages['confirm_comment']}"
        )
        add_pr_comment(comment)
        
        print("::set-output name=changes_detected::true")
    else:
        print(messages['no_changes'])
        print("::set-output name=changes_detected::false")

if __name__ == "__main__":
    main()