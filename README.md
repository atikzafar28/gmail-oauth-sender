# Gmail OAuth2 Email Sender

Send emails using Gmail with OAuth2 authentication. Supports PDF and other attachments.

## Setup

1. Create a Google Cloud Project.
2. Enable Gmail API.
3. Configure OAuth consent screen (External, add your email as test user).
4. Create OAuth Client ID (Desktop App).
5. Download `credentials.json` and place in project folder.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
