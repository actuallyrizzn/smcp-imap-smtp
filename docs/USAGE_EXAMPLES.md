# Usage Examples

## IMAP Tool Examples

### Connect to IMAP Server

```bash
python tools/imap/cli.py connect --server imap.gmx.com --username SMCPtest1@gmx.com --password "IL6Y3ZBOFBJ7XIDIPT45"
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "server": "imap.gmx.com",
    "username": "SMCPtest1@gmx.com",
    "port": 993,
    "ssl": true,
    "connected": true
  }
}
```

### List Mailboxes

```bash
python tools/imap/cli.py list-mailboxes
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "mailboxes": [
      {"name": "INBOX", "delimiter": "/", "flags": []},
      {"name": "Sent", "delimiter": "/", "flags": []},
      {"name": "Drafts", "delimiter": "/", "flags": []}
    ]
  }
}
```

### Select Mailbox and Search

```bash
python tools/imap/cli.py select-mailbox --mailbox INBOX
python tools/imap/cli.py search --criteria "ALL"
```

**Search Response:**
```json
{
  "status": "success",
  "result": {
    "criteria": "ALL",
    "message_ids": [1, 2, 3, 4, 5],
    "count": 5
  }
}
```

### Fetch Email

```bash
python tools/imap/cli.py fetch --message-id 1
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "id": "1",
    "mailbox": "INBOX",
    "from": {
      "name": "Sender Name",
      "email": "sender@example.com"
    },
    "to": [{"name": "", "email": "SMCPtest1@gmx.com"}],
    "subject": "Test Subject",
    "timestamp": "2025-12-03T00:30:00Z",
    "body": {
      "text": "Email body text",
      "html": "",
      "attachments": []
    },
    "headers": {
      "message-id": "<message-id>",
      "date": "Mon, 2 Dec 2025 12:00:00 +0000"
    },
    "flags": []
  }
}
```

### Mark as Read/Unread (Sandbox Mode)

```bash
# Simulate marking as read (sandbox mode)
python tools/imap/cli.py mark-read --message-ids 1 2 --sandbox

# Actually mark as read
python tools/imap/cli.py mark-read --message-ids 1 2
```

## SMTP Tool Examples

### Connect to SMTP Server

```bash
python tools/smtp/cli.py connect --server mail.gmx.com --username SMCPtest1@gmx.com --password "IL6Y3ZBOFBJ7XIDIPT45" --port 587
```

### Send Plain Text Email

```bash
python tools/smtp/cli.py send --to recipient@example.com --subject "Test Email" --body "Hello, this is a test email."
```

### Send HTML Email

```bash
python tools/smtp/cli.py send-html --to recipient@example.com --subject "HTML Test" --html-body "<html><body><h1>Hello</h1><p>This is HTML.</p></body></html>"
```

### Send Email with Attachments

```bash
python tools/smtp/cli.py send-with-attachment --to recipient@example.com --subject "With Attachment" --body "See attachment" --attachments file1.pdf file2.jpg
```

## UCW Wrapping Examples

### Wrap IMAP Tool

```bash
python ucw/cli.py wrap tools/imap/cli.py --output plugins/imap/cli.py
```

### Wrap SMTP Tool

```bash
python ucw/cli.py wrap tools/smtp/cli.py --output plugins/smtp/cli.py
```

### Use Wrapped Plugin

```bash
python plugins/imap/cli.py execute connect --server imap.gmx.com --username SMCPtest1@gmx.com --password "IL6Y3ZBOFBJ7XIDIPT45"
```

## Error Handling Examples

### Authentication Failure

```bash
python tools/imap/cli.py connect --server imap.gmx.com --username wrong@example.com --password "wrong"
```

**Response:**
```json
{
  "error": "Connection failed: Authentication failed. This may be due to:\n1. Incorrect username or password\n2. IMAP access may not be enabled in account settings\n3. App password may be incorrect or expired\n4. Account may need additional security setup\nOriginal error: b'authentication failed'"
}
```

### Not Connected Error

```bash
python tools/imap/cli.py list-mailboxes
```

**Response:**
```json
{
  "error": "Not connected to IMAP server"
}
```

