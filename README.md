# YouTube Subscription Migrator

A simple Python script to copy all YouTube channel subscriptions from one Google account to another.

## Prerequisites

- Python 3.7 or higher  
- Poetry (https://python-poetry.org/)
- A Google Cloud OAuth 2.0 **Client Secrets JSON** file with both **YouTube Data API v3 (readonly)** and **YouTube Data API v3 (write)** scopes enabled.

## Usage

1. Clone this repository:
```bash
    git clone https://github.com/kebi-kim/YouTube-Migration.git
    cd YouTube-Migration
```
2. Install dependencies:
```bash
    poetry install
```

3. Run the script:
```bash
    python migrate_subscriptions.py client_secrets.json
```