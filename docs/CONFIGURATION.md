# Configuration Guide

## Server Configurations

### GMX (Primary Testing)

**IMAP Settings:**
- Server: `imap.gmx.com`
- Port: `993`
- Encryption: SSL/TLS
- Username: Full email address (e.g., `SMCPtest1@gmx.com`)
- Password: App-specific password (if 2FA enabled) or regular password

**SMTP Settings:**
- Server: `mail.gmx.com`
- Port: `587` (STARTTLS) or `465` (SSL)
- Encryption: STARTTLS or SSL/TLS
- Username: Full email address
- Password: Same as IMAP

**Requirements:**
- IMAP must be enabled in Settings > POP3 & IMAP
- 2FA must be enabled for app-specific passwords
- Allow 5-15 minutes for IMAP activation after enabling

### AOL (Backup/Reference)

**IMAP Settings:**
- Server: `imap.aol.com`
- Port: `993`
- Encryption: SSL/TLS
- Username: Full email address
- Password: App-specific password (required)

**SMTP Settings:**
- Server: `smtp.aol.com`
- Port: `587` (STARTTLS) or `465` (SSL)
- Encryption: STARTTLS or SSL/TLS
- Username: Full email address
- Password: App-specific password (required)

**Requirements:**
- AOL requires app passwords for IMAP/SMTP
- Generate app password from Account Security page

### Gmail (Reference)

**IMAP Settings:**
- Server: `imap.gmail.com`
- Port: `993`
- Encryption: SSL/TLS
- Username: Full email address
- Password: App password (if 2FA enabled)

**SMTP Settings:**
- Server: `smtp.gmail.com`
- Port: `587` (STARTTLS) or `465` (SSL)
- Encryption: STARTTLS or SSL/TLS
- Username: Full email address
- Password: App password

## Environment Variables

For secure credential storage, you can use environment variables:

```bash
# Windows PowerShell
$env:IMAP_USERNAME="SMCPtest1@gmx.com"
$env:IMAP_PASSWORD="IL6Y3ZBOFBJ7XIDIPT45"

# Linux/macOS
export IMAP_USERNAME="SMCPtest1@gmx.com"
export IMAP_PASSWORD="IL6Y3ZBOFBJ7XIDIPT45"
```

Then use in commands:
```bash
python tools/imap/cli.py connect --server imap.gmx.com --username $env:IMAP_USERNAME --password $env:IMAP_PASSWORD
```

## Guardrails Configuration

### Size Limits

Default limits (can be adjusted in code):
- `MAX_BODY_BYTES`: 10MB (email body)
- `MAX_ATTACHMENT_BYTES`: 25MB (attachments)

### Sandbox Mode

Enable sandbox mode to prevent destructive operations:
- `--sandbox` flag on delete, move, mark-read, mark-unread commands
- Simulates operations without actually executing them
- Returns `"status": "sandbox"` with `would_*` fields

## UCW Configuration

### Wrapping CLI Tools

```bash
# Wrap IMAP tool
python ucw/cli.py wrap tools/imap/cli.py --output plugins/imap/cli.py

# Wrap SMTP tool
python ucw/cli.py wrap tools/smtp/cli.py --output plugins/smtp/cli.py
```

### Testing Wrapped Plugins

```bash
# Test wrapped IMAP plugin
python plugins/imap/cli.py execute connect --server imap.gmx.com --username test@gmx.com --password pass

# Test wrapped SMTP plugin
python plugins/smtp/cli.py execute connect --server mail.gmx.com --username test@gmx.com --password pass
```

## SMCP Server Integration

### Plugin Discovery

SMCP servers automatically discover plugins in the `plugins/` directory.

### Tool Registration

Wrapped plugins are automatically registered as SMCP tools with:
- Command names from argparse subcommands
- Parameter schemas from argument definitions
- Help text from command descriptions

### Usage in SMCP

Once wrapped and registered, tools can be called by AI agents:
- Tool name: `imap_connect`, `imap_list_mailboxes`, etc.
- Parameters: Automatically mapped from CLI arguments
- Response: JSON output from CLI tool

