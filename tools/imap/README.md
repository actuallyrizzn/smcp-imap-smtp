# IMAP CLI Tool

A command-line tool for IMAP email operations that can be wrapped by UCW (Universal Command Wrapper) to become an SMCP plugin.

## Overview

This tool provides full-featured email reading capabilities including:
- Connecting to IMAP servers
- Listing and selecting mailboxes
- Searching and fetching emails
- Managing email flags (read/unread)
- Moving and deleting emails (with sandbox mode support)

## Installation

This tool requires Python 3.7+ and the following dependencies:

```bash
pip install imapclient
```

## Usage

### Connect to IMAP Server

```bash
python tools/imap/cli.py connect --server imap.aol.com --username test@aol.com --password yourpassword
```

### List Mailboxes

```bash
python tools/imap/cli.py list-mailboxes
```

### Select Mailbox

```bash
python tools/imap/cli.py select-mailbox --mailbox INBOX
```

### Search Emails

```bash
python tools/imap/cli.py search --criteria "ALL"
python tools/imap/cli.py search --criteria "UNSEEN"
python tools/imap/cli.py search --criteria "FROM sender@example.com"
```

### Fetch Email

```bash
python tools/imap/cli.py fetch --message-id 12345
```

### Mark as Read/Unread

```bash
python tools/imap/cli.py mark-read --message-ids 12345 12346
python tools/imap/cli.py mark-unread --message-ids 12345
```

### Delete Emails (Sandbox Mode)

```bash
# Simulate deletion (sandbox mode)
python tools/imap/cli.py delete --message-ids 12345 --sandbox

# Actually delete
python tools/imap/cli.py delete --message-ids 12345
```

### Move Emails (Sandbox Mode)

```bash
# Simulate move (sandbox mode)
python tools/imap/cli.py move --message-ids 12345 --target-mailbox Archive --sandbox

# Actually move
python tools/imap/cli.py move --message-ids 12345 --target-mailbox Archive
```

## Output Format

All commands output JSON:

**Success:**
```json
{
  "status": "success",
  "result": {
    "data": "..."
  }
}
```

**Error:**
```json
{
  "error": "Error message"
}
```

**Sandbox Mode:**
```json
{
  "status": "sandbox",
  "result": {
    "would_delete": true,
    "sandbox_mode": true
  }
}
```

## UCW Integration

This tool is designed to be wrapped by UCW. To wrap it:

```bash
python ucw/cli.py wrap tools/imap/cli.py --output plugins/imap/cli.py
```

## Development Status

This is a work in progress. Core functionality is being implemented according to the project plan.

## License

GNU Affero General Public License v3.0

