# Installation and Setup Guide

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/actuallyrizzn/smcp-imap-smtp.git
cd smcp-imap-smtp
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `imapclient` - IMAP client library
- `pytest` - Testing framework (optional, for development)

### 4. Verify Installation

```bash
# Test IMAP CLI
python tools/imap/cli.py --help

# Test SMTP CLI
python tools/smtp/cli.py --help
```

## Using the CLI Tools Directly

### IMAP Tool

```bash
# Connect to IMAP server
python tools/imap/cli.py connect --server imap.gmx.com --username your@email.com --password yourpassword

# List mailboxes
python tools/imap/cli.py list-mailboxes

# Search emails
python tools/imap/cli.py search --criteria "ALL"

# Fetch email
python tools/imap/cli.py fetch --message-id 1
```

### SMTP Tool

```bash
# Connect to SMTP server
python tools/smtp/cli.py connect --server mail.gmx.com --username your@email.com --password yourpassword

# Send email
python tools/smtp/cli.py send --to recipient@example.com --subject "Test" --body "Hello"
```

## Wrapping with UCW for SMCP Integration

### 1. Install UCW (if not already installed)

```bash
git clone https://github.com/actuallyrizzn/ucw.git
cd ucw
pip install -r requirements.txt
```

### 2. Wrap IMAP Tool

```bash
python ucw/cli.py wrap tools/imap/cli.py --output plugins/imap/cli.py
```

### 3. Wrap SMTP Tool

```bash
python ucw/cli.py wrap tools/smtp/cli.py --output plugins/smtp/cli.py
```

### 4. Use Wrapped Plugins

Wrapped plugins can be used directly or registered with SMCP server:

```bash
# Direct usage
python plugins/imap/cli.py execute connect --server imap.gmx.com --username your@email.com --password yourpassword

# Or register with SMCP server (see SMCP documentation)
```

## Environment Variables (Optional)

For secure credential storage:

```bash
# Windows PowerShell
$env:IMAP_USERNAME="your@email.com"
$env:IMAP_PASSWORD="yourpassword"
$env:SMTP_USERNAME="your@email.com"
$env:SMTP_PASSWORD="yourpassword"

# Linux/macOS
export IMAP_USERNAME="your@email.com"
export IMAP_PASSWORD="yourpassword"
export SMTP_USERNAME="your@email.com"
export SMTP_PASSWORD="yourpassword"
```

Then use in commands:
```bash
python tools/imap/cli.py connect --server imap.gmx.com --username $env:IMAP_USERNAME --password $env:IMAP_PASSWORD
```

## Configuration

### Email Server Settings

See [CONFIGURATION.md](CONFIGURATION.md) for server-specific settings:
- GMX
- AOL
- Gmail
- Generic IMAP/SMTP servers

### Guardrails

Size limits can be configured via environment variables:
```bash
export MAX_BODY_BYTES=10485760      # 10MB
export MAX_ATTACHMENT_BYTES=26214400  # 25MB
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Next Steps

- Read [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for detailed examples
- Review [CONFIGURATION.md](CONFIGURATION.md) for server settings
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you encounter issues

