# Codex Reset Monitor

This project monitors public X posts from Tibo and any additional configured accounts, detects possible Codex reset announcements, deduplicates alerts, and sends email notifications through SMTP.

It is designed to run on GitHub Actions without paid X API access.

## How It Works

1. GitHub Actions runs the monitor on a schedule.
2. The monitor fetches the latest public post through an RSS/Atom feed.
3. It checks whether the post is new for that account.
4. It runs keyword filtering.
5. Optionally, it asks an OpenAI model to classify whether the post is really about a Codex usage reset.
6. If relevant, it sends an email alert.
7. It updates `data/state.json` so the same post is not sent again.

## Public Data Source

The default source is RSSHub:

```text
https://rsshub.app/twitter/user/{handle}
```

This avoids paid X API access, but it has important limitations:

- It depends on RSSHub's public instance availability.
- X can rate-limit, block, or change public access behavior.
- Public RSSHub instances may be slower or less reliable than a self-hosted RSSHub instance.
- The feed may not include deleted posts, replies, reposts, or all metadata.
- GitHub Actions scheduled workflows are not guaranteed to run exactly on the minute.

For better reliability, self-host RSSHub and set the optional `RSSHUB_BASE_URL` secret to your instance URL, for example:

```text
RSSHUB_BASE_URL=https://your-rsshub.example.com
```

You can also replace `url_template` in `config.yaml` with another public RSS/Atom-compatible feed source.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with your SMTP settings.

Run tests:

```bash
pytest
```

Run a local dry run:

```bash
DRY_RUN=true python -m src.monitor
```

On Windows PowerShell:

```powershell
$env:DRY_RUN="true"
python -m src.monitor
```

## Gmail SMTP Setup

Recommended Gmail settings:

```text
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-sender@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-sender@gmail.com
EMAIL_TO=your-recipient@gmail.com
```

Use a Gmail App Password, not your normal Gmail login password. Gmail App Passwords require two-step verification on the Google account.

## GitHub Secrets

Add these in your GitHub repository:

```text
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
EMAIL_FROM
EMAIL_TO
```

Optional:

```text
EMAIL_CC
USE_LLM_CLASSIFIER
OPENAI_API_KEY
OPENAI_MODEL
RSSHUB_BASE_URL
```

Example optional LLM values:

```text
USE_LLM_CLASSIFIER=true
OPENAI_MODEL=gpt-5-mini
```

If `USE_LLM_CLASSIFIER` is false or unset, the project uses keyword filtering only.

## GitHub Actions Schedule

The workflow is configured in `.github/workflows/monitor.yml`:

```yaml
schedule:
  - cron: "*/5 * * * *"
```

GitHub Actions generally does not support reliable one-minute polling for scheduled workflows. Five minutes is the practical default. You can also run the workflow manually with `workflow_dispatch`.

## Monitoring More Accounts

Edit `config.yaml`:

```yaml
accounts:
  - name: Tibo
    handle: thsottiaux
    url_template: "{rsshub_base_url}/twitter/user/{handle}"
  - name: OpenAI
    handle: OpenAI
    url_template: "{rsshub_base_url}/twitter/user/{handle}"
```

Each account gets its own last-seen post ID in `data/state.json`.

## Keyword Tuning

Edit `config.yaml`:

```yaml
keywords:
  any:
    - reset
    - codex
    - usage limit
    - usage limits
    - quota
  required_any:
    - codex
    - usage
    - reset
```

`any` contains terms that can trigger attention.

`required_any` is a second-pass context check. At least one of these terms must also appear, which helps avoid unrelated posts such as password resets or bank messages.

## Optional LLM Classification

Keyword filtering is cheap and fast, but it can still produce false positives. Enable the optional LLM step when you want fewer false alerts:

```text
USE_LLM_CLASSIFIER=true
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-5-mini
```

The LLM is only called after keyword filtering has already matched, which keeps cost low.

## State and Deduplication

`data/state.json` stores the latest seen post ID per account. The GitHub workflow commits changes to this file after each run.

This means:

- The same post will not generate repeated emails.
- A non-relevant new post is also marked as seen.
- If you delete or reset `data/state.json`, old feed entries may alert again.

## Files

```text
.github/workflows/monitor.yml
config.yaml
data/state.json
requirements.txt
src/config.py
src/feed_source.py
src/filtering.py
src/classifier.py
src/emailer.py
src/state.py
src/monitor.py
tests/test_filtering.py
.env.example
```
