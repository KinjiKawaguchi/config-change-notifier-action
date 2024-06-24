# Config Change Notifier Action

This GitHub Action detects changes in specified config files and ensures team notification.

## Usage

```yaml
- uses: KinjiKawaguchi/config-change-notifier-action@v1
  with:
    config_files: |
      config/database.yml
      config/application.yml
      .env.example
      src/config/settings.js
