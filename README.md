# Cardinals Lineup Bot

A GitHub Actions bot that emails the St. Louis Cardinals starting lineup each game day as soon as it's posted on MLB.

## How it works

1. Runs daily at noon CDT (April–October) via GitHub Actions
2. Checks the MLB Stats API for a Cardinals game that day
3. Polls every 15 minutes (up to 5 hours) until the lineup is officially posted
4. Sends an email with the batting order to all configured recipients

## Setup

### 1. Add the Gmail secret

In your GitHub repo, go to **Settings → Secrets and variables → Actions** and add:

| Secret name | Value |
|---|---|
| `EMAIL_APP_PASSWORD` | A [Gmail App Password](https://support.google.com/accounts/answer/185833) for the sender account |

> Regular Gmail passwords won't work — you need a 16-character App Password with 2FA enabled on the account.

### 2. Configure recipients

Edit `cards_lineup.py` and update the `RECEIVER_EMAIL` list:

```python
SENDER_EMAIL = "you@gmail.com"
RECEIVER_EMAIL = ["you@gmail.com", "someone@example.com"]
```

### 3. Enable the workflow

Push to `main`. The workflow will trigger automatically every day at noon CDT from April through October. You can also run it manually from the **Actions** tab using the "Run workflow" button.

## Local usage

```bash
pip install -r requirements.txt
EMAIL_APP_PASSWORD=your_app_password python cards_lineup.py
```
