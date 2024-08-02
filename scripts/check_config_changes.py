import os
import requests
import logging
from typing import List, Dict
from slack_sdk.webhook import WebhookClient
from slack_sdk.models.blocks import HeaderBlock, SectionBlock, DividerBlock, ActionsBlock
from slack_sdk.models.blocks.block_elements import ButtonElement

# ロガーの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_config_files() -> List[str]:
    config_files_str = os.environ.get('CONFIG_FILES', '')
    config_files = [file.strip() for file in config_files_str.split('\n') if file.strip()]
    logger.info(f"Retrieved config files: {config_files}")
    return config_files

def check_file_changes(file_path: str) -> Dict[int, str]:
    """
    check_file_changes 関数の挙動説明:
    この関数は指定されたファイルの変更内容を分析し、新しく追加された行を特定します。
    主な処理の流れ:
    1. git diff コマンドを使用して、origin/main ブランチと HEAD の間の指定されたファイルの差分を取得します。
    2. diff 出力を行ごとに解析し、新しく追加された行を識別します。
    3. 新しい行の行番号と内容を辞書形式で返します。

    詳細な解析プロセス:
    - diff 出力のヘッダー部分（'@@'行が出現するまで）はスキップされます。
    - '@@'行が見つかると、そこから実際の変更内容の解析が始まります。
    - '@@'行から現在の行番号を抽出します（例: '@@ -1,7 +1,9 @@' から '+1' を取得）。
    - '+'で始まる行は新しく追加された行として処理されます。
    - ただし、'+++'で始まる行（ファイル名を示す行）は無視されます。
    - '-'で始まる行（削除された行）は無視されますが、行番号はインクリメントされません。
    - その他の行（変更されていない行）に対しては、行番号のみがインクリメントされます。

    戻り値:
    - 辞書形式で、キーが行番号、値が追加された行の内容となります。

    注意点:
    - この関数は新しく追加された行のみを返します。変更された行や削除された行は結果に含まれません。
    - git diff の出力形式に依存しているため、git の仕様変更があった場合は動作が変わる可能性があります。
    - ログ出力を使用して、処理の各ステップを詳細に記録しています。
    """
    logger.info(f"Checking changes for file: {file_path}")
    diff_output = os.popen(f'git diff origin/main..HEAD -- {file_path}').read()
    logger.debug(f"Raw diff output:\n{diff_output}")

    changes = {}
    current_line = 0
    in_header = True
    for line in diff_output.split('\n'):
        logger.debug(f"Processing line: {line}")
        if line.startswith('@@'):
            logger.debug("Found @@ line (chunk header)")
            in_header = False
            line_info = line.split()[2]
            logger.debug(f"Line info: {line_info}")
            current_line = int(line_info.split(',')[0].lstrip('+'))
            logger.debug(f"Updated current_line to: {current_line}")
        elif not in_header and line.startswith('+'):
            if not line.startswith('+++'):
                changes[current_line] = line[1:]
                logger.debug(f"Added change at line {current_line}: {line[1:]}")
            current_line += 1
        elif not line.startswith('-'):
            current_line += 1

    logger.debug(f"Final changes dict: {changes}")
    return changes

def add_pr_review(file_path: str, line: int, comment: str):
    pr_number = os.environ.get('PR_NUMBER')
    token = os.environ.get('GITHUB_TOKEN')
    if not pr_number or not token:
        logger.warning("PR number or GitHub token is not set.")
        return
    logger.info(f"Adding PR review for file: {file_path}, line: {line}")
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
    if response.status_code == 200:
        logger.info("Successfully added PR review")
    else:
        logger.error(f"Failed to add PR review: {response.text}")

def get_localized_messages() -> Dict[str, str]:
    language = os.environ.get('LANGUAGE', 'en')
    logger.info(f"Using language: {language}")
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



def send_slack_notification(file_path: str, changes: Dict[int, str], messages: Dict[str, str]):
    webhook_url = os.environ.get('SLACK_WEBHOOK')
    if not webhook_url:
        logger.warning("Slack webhook URL is not set.")
        return
    logger.info(f"Sending Slack notification for file: {file_path}")
    
    webhook = WebhookClient(webhook_url)
    
    blocks = [
        HeaderBlock(text="設定ファイルの変更が検出されました"),
        SectionBlock(text=f"*ファイル:* `{file_path}`"),
        DividerBlock()
    ]
    
    for line, content in changes.items():
        blocks.append(SectionBlock(text=f"*行 {line}:*\n```{content}```"))
    
    blocks.append(ActionsBlock(
        elements=[
            ButtonElement(
                text="PRを確認",
                url=f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/pull/{os.environ.get('PR_NUMBER')}"
            )
        ]
    ))
    
    response = webhook.send(blocks=blocks)
    
    if response.status_code == 200:
        logger.info("Successfully sent Slack notification")
    else:
        logger.error(f"Failed to send Slack notification: {response.body}")

def notify_changes(file_path: str, changes: Dict[int, str], messages: Dict[str, str]):
    notification_method = os.environ.get('NOTIFICATION_METHOD', 'pr_comment')
    logger.info(f"Using notification method: {notification_method}")
    
    if notification_method in ['pr_comment', 'both']:
        for line, content in changes.items():
            comment = f"{messages['review_required']}\nChanged content: {content}"
            add_pr_review(file_path, line, comment)
    
    if notification_method in ['slack', 'both']:
        send_slack_notification(file_path, changes, messages)

def main():
    logger.info("Starting main function")
    config_files = get_config_files()
    messages = get_localized_messages()
    changes_detected = False
    
    for file in config_files:
        logger.info(f"Checking file: {file}")
        changes = check_file_changes(file)
        if changes:
            changes_detected = True
            logger.info(f"{messages['changes_detected']} {file}")
            logger.info(f"Changes: {changes}")
            notify_changes(file, changes, messages)
    
    if changes_detected:
        logger.info("Changes detected in at least one file")
        logger.info("::set-output name=changes_detected::true")
    else:
        logger.info(messages['no_changes'])
        logger.info("::set-output name=changes_detected::false")
    
    logger.info("Finished main function")

if __name__ == "__main__":
    main()