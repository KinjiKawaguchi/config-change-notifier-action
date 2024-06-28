import os
import yaml
import sys
import requests
from typing import List, Dict


def get_config_files() -> List[str]:
    config_files_str = os.environ.get('CONFIG_FILES', '')
    return [file.strip() for file in config_files_str.split('\n') if file.strip()]


def check_file_changes(file_path: str) -> Dict[int, str]:
    print(f"Checking changes for file: {file_path}")
    diff_output = os.popen(f'git diff origin/main..HEAD -- {file_path}').read()
    print(f"Raw diff output:\n{diff_output}")

    changes = {}
    current_line = 0
    for line in diff_output.split('\n'):
        print(f"Processing line: {line}")
        if line.startswith('@@'):
            print("Found @@ line (chunk header)")
            line_info = line.split()[2]
            print(f"Line info: {line_info}")
            current_line = int(line_info.split(',')[0].lstrip('+')) - 1
            print(f"Updated current_line to: {current_line}")
        elif line.startswith('+'):
            current_line += 1
            changes[current_line] = line[1:]
            print(f"Added change at line {current_line}: {line[1:]}")
        else:
            print("Skipping line (not a change)")

    print(f"Final changes dict: {changes}")
    return changes


def add_pr_review(file_path: str, line: int, comment: str):
    pr_number = os.environ.get('PR_NUMBER')
    token = os.environ.get('GITHUB_TOKEN')
    if not pr_number or not token:
        print("PR number or GitHub token is not set.")
        return
    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/pulls/{pr_number}/reviews"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": comment,
        "event": "COMMENT",
        "comments": [
            {
                "path": file_path,
                "position": line,
                "body": comment
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        print(f"Failed to add PR review: {response.text}")


def get_localized_messages() -> Dict[str, str]:
    language = os.environ.get('LANGUAGE', 'en')
    messages = {
        'en': {
            'changes_detected': "Changes detected in the following config file:",
            'review_required': "ChangeRequired: Please review this change.",
            'no_changes': "No changes detected in config files."
        },
        'ja': {
            'changes_detected': "以下の設定ファイルに変更が検出されました：",
            'review_required': "要変更: この変更を確認してください。",
            'no_changes': "設定ファイルに変更は検出されませんでした。"
        }
    }
    return messages.get(language, messages['en'])


def main():
    config_files = get_config_files()
    messages = get_localized_messages()
    changes_detected = False

    for file in config_files:
        changes = check_file_changes(file)
        if changes:
            changes_detected = True
            print(f"{messages['changes_detected']} {file}")
            for line, content in changes.items():
                comment = f"{messages['review_required']}\nChanged content: {content}"
                add_pr_review(file, line, comment)

    if changes_detected:
        print("::set-output name=changes_detected::true")
    else:
        print(messages['no_changes'])
        print("::set-output name=changes_detected::false")


if __name__ == "__main__":
    main()
