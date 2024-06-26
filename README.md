# Config Change Notifier Action

This GitHub Action detects changes in specified config files and ensures team notification.
設定ファイルの変更を検出し、チームへの通知を確実にするGitHub Actionです。

## Usage / 使用方法

```yaml
- uses: KinjiKawaguchi/config-change-notifier-action@v1.2
  with:
    config_files: |
      config/database.yml
      config/application.yml
      .env.example
      src/config/settings.js
    language: 'en'  # Optional: 'en' (default) or 'ja' for Japanese
```

## Inputs / 入力

| Name / 名前 | Description / 説明 | Required / 必須 | Default / デフォルト |
|-------------|---------------------|------------------|----------------------|
| `config_files` | List of config files to monitor<br>監視する設定ファイルのリスト | Yes / はい | N/A |
| `language` | Notification language<br>通知の言語 | No / いいえ | 'en' |

## Supported Languages / 対応言語

| Language Code / 言語コード | Language / 言語 |
|----------------------------|-----------------|
| `en` | English / 英語 |
| `ja` | Japanese / 日本語 |

## How it works / 動作の仕組み

1. The action checks for changes in the specified config files.
2. If changes are detected, it adds a comment to the PR with the list of changed files.
3. It requests confirmation that the changes have been shared with the team.
4. The action waits indefinitely for the confirmation command to be commented.
5. Once the exact confirmation command is received, the action completes successfully.

---

1. 指定された設定ファイルの変更をチェックします。
2. 変更が検出された場合、変更されたファイルのリストとともにPRにコメントを追加します。
3. 変更がチームと共有されたことの確認を要求します。
4. アクションは確認コマンドがコメントされるまで無期限に待機します。
5. 正確な確認コマンドが受信されると、アクションは正常に完了します。

## Confirmation Command / 確認コマンド

After sharing the config changes with the team, comment the following on the PR:
設定変更をチームと共有した後、PRに以下のようにコメントしてください：

```
/config-change-notified
```

This command confirms that the team has been notified of the config changes.
このコマンドは、設定変更についてチームに通知されたことを確認します。

**Note**: The confirmation command must be exactly as shown above. Comments containing this command as part of a larger message will not be accepted.
**注意**: 確認コマンドは上記のとおり正確に入力する必要があります。このコマンドを含む大きなメッセージは受け付けられません。

## License / ライセンス

[MIT License](LICENSE)