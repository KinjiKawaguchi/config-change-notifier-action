# Config Change Notifier Action

This GitHub Action detects changes in specified config files and ensures team notification via PR comments and/or Slack.

設定ファイルの変更を検出し、PRコメントやSlackを通じてチームへの通知を確実にするGitHub Actionです。

## Usage / 使用方法

```yaml
- uses: KinjiKawaguchi/config-change-notifier-action@v1.0
  with:
    config_files: |
      config/database.yml
      config/application.yml
      .env.example
      src/config/settings.js
    language: 'en'
    notification_method: 'both'
    slack_webhook: ${{ secrets.SLACK_WEBHOOK }}
```

## Inputs / 入力

| Name / 名前 | Description / 説明 | Required / 必須 | Default / デフォルト |
|-------------|---------------------|------------------|----------------------|
| `config_files` | List of config files to monitor<br>監視する設定ファイルのリスト | Yes / はい | N/A |
| `language` | Notification language<br>通知の言語 | No / いいえ | 'en' |
| `notification_method` | Notification method<br>通知方法 | No / いいえ | 'pr_comment' |
| `slack_webhook` | Slack webhook URL for notifications<br>Slack通知用のwebhook URL | No / いいえ | N/A |

## Supported Languages / 対応言語

| Language Code / 言語コード | Language / 言語 |
|----------------------------|-----------------|
| `en` | English / 英語 |
| `ja` | Japanese / 日本語 |

## Notification Methods / 通知方法

| Method Code / 方法コード | Description / 説明 |
|--------------------------|---------------------|
| `pr_comment` | Adds comments to the PR for each changed file<br>変更された各ファイルについてPRにコメントを追加します |
| `slack` | Sends a notification to Slack with details of the changes<br>変更の詳細をSlackに通知します |
| `both` | Uses both PR comments and Slack notifications<br>PRコメントとSlack通知の両方を使用します |

## How it works / 動作の仕組み

1. The action checks for changes in the specified config files.
2. If changes are detected, it notifies via the specified method(s):
   - Adds comments to the PR for each changed file (if 'pr_comment' or 'both' is selected).
   - Sends a notification to Slack with details of the changes (if 'slack' or 'both' is selected).
3. The action completes after sending the notifications.

---

1. 指定された設定ファイルの変更をチェックします。
2. 変更が検出された場合、指定された方法で通知します：
   - 変更された各ファイルについてPRにコメントを追加します（'pr_comment'または'both'が選択された場合）。
   - 変更の詳細をSlackに通知します（'slack'または'both'が選択された場合）。
3. 通知の送信後、アクションは完了します。

## Slack Notification / Slack通知

If Slack notification is enabled, the action will send a message to the specified Slack channel with:
- The name of the changed config file
- Details of the changes
- A button to view the PR

Slack通知が有効な場合、アクションは指定されたSlackチャンネルに以下の内容のメッセージを送信します：
- 変更された設定ファイルの名前
- 変更の詳細
- PRを表示するためのボタン

## License / ライセンス

[MIT License](LICENSE)
