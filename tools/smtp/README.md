# SMTP CLI Tool

A command-line tool for SMTP email operations that can be wrapped by UCW (Universal Command Wrapper) to become an SMCP plugin.

## Overview

This tool provides full-featured email sending capabilities including:
- Connecting to SMTP servers
- Sending plain text emails
- Sending HTML emails
- Sending emails with attachments
- Support for CC, BCC, Reply-To headers
- Authentication (TLS/SSL)

## Installation

This tool requires Python 3.7+ and uses the standard library `smtplib` (no external dependencies required).

## Usage

### Connect to SMTP Server

```bash
python tools/smtp/cli.py connect --server smtp.aol.com --username test@aol.com --password yourpassword
```

### Send Plain Text Email

```bash
python tools/smtp/cli.py send --to recipient@example.com --subject "Test" --body "Hello, world!"
```

### Send HTML Email

```bash
python tools/smtp/cli.py send-html --to recipient@example.com --subject "Test" --html-body "<html><body><h1>Hello</h1></body></html>"
```

### Send Email with Attachments

```bash
python tools/smtp/cli.py send-with-attachment --to recipient@example.com --subject "Test" --body "See attachment" --attachments file1.pdf file2.jpg
```

## Output Format

All commands output JSON:

**Success:**
```json
{
  "status": "success",
  "result": {
    "sent": true,
    "from": "sender@example.com",
    "to": ["recipient@example.com"],
    "subject": "Test"
  }
}
```

**Error:**
```json
{
  "error": "Error message"
}
```

## UCW Integration

This tool is designed to be wrapped by UCW. To wrap it:

```bash
python ucw/cli.py wrap tools/smtp/cli.py --output plugins/smtp/cli.py
```

## Guardrails

- Maximum attachment size: 25MB (configurable via `MAX_ATTACHMENT_BYTES`)
- Attachment size validation before sending
- File existence validation

## Development Status

This is a work in progress. Core functionality is being implemented according to the project plan.

## License

GNU Affero General Public License v3.0

