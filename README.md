# SMCP IMAP/SMTP Tools

Command-line tools for IMAP (email reading) and SMTP (email sending) that can be wrapped by UCW (Universal Command Wrapper) to become SMCP plugins.

## Overview

This project provides two CLI tools:
- **IMAP Tool**: Full-featured email reading capabilities
- **SMTP Tool**: Full-featured email sending capabilities

Both tools are designed to be wrapped by UCW, making them instantly usable as SMCP plugins for AI agents.

## Quick Start

### Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**:
   
   **Windows (PowerShell)**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   **Linux/macOS**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

#### IMAP Tool

```bash
# Connect to IMAP server
python tools/imap/cli.py connect --server imap.aol.com --username test@aol.com --password pass

# List mailboxes
python tools/imap/cli.py list-mailboxes

# Search emails
python tools/imap/cli.py search --criteria "ALL"

# Fetch email
python tools/imap/cli.py fetch --message-id 12345
```

#### SMTP Tool

```bash
# Connect to SMTP server
python tools/smtp/cli.py connect --server smtp.aol.com --username test@aol.com --password pass

# Send email
python tools/smtp/cli.py send --to recipient@example.com --subject "Test" --body "Hello"
```

## UCW Wrapping

Both tools can be wrapped by UCW to become SMCP plugins:

```bash
# Wrap IMAP tool
python ucw/cli.py wrap tools/imap/cli.py --output plugins/imap/cli.py

# Wrap SMTP tool
python ucw/cli.py wrap tools/smtp/cli.py --output plugins/smtp/cli.py
```

## Project Structure

```
smcp-imap-smtp/
├── tools/              # CLI tools
│   ├── imap/          # IMAP email reading tool
│   └── smtp/          # SMTP email sending tool
├── docs/              # Documentation
├── tmp/               # Temporary files (git-ignored)
├── venv/              # Virtual environment (git-ignored)
├── requirements.txt   # Python dependencies
└── SETUP.md           # Setup instructions
```

## Features

### IMAP Tool
- Connect to IMAP servers
- List and select mailboxes
- Search emails
- Fetch email content with normalization
- Mark emails as read/unread
- Delete and move emails (with sandbox mode)
- Guardrails: MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES

### SMTP Tool
- Connect to SMTP servers
- Send plain text emails
- Send HTML emails
- Send emails with attachments
- Support for CC, BCC, Reply-To headers
- Guardrails: MAX_ATTACHMENT_BYTES

## Related Projects

- **[SMCP (SanctumOS)](https://github.com/sanctumos/smcp)** - SanctumOS Model Context Protocol server
- **[SMCP (Animus)](https://github.com/AnimusUNO/smcp)** - Animus Model Context Protocol server
- **[UCW (Universal Command Wrapper)](https://github.com/actuallyrizzn/ucw)** - Universal Command Wrapper for wrapping CLI tools into SMCP plugins

## Documentation

- [Project Plan](docs/PROJECT_PLAN.md) - Detailed development plan
- [Installation Guide](docs/INSTALLATION.md) - Installation and setup instructions
- [Usage Examples](docs/USAGE_EXAMPLES.md) - Detailed usage examples
- [Configuration Guide](docs/CONFIGURATION.md) - Server configurations and settings
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [UCW Requirements](docs/UCW_REQUIREMENTS.md) - UCW compatibility requirements
- [Email Protocol Spec](docs/EMAIL_PROTOCOL_SPEC.md) - Technical specifications
- [Setup Instructions](SETUP.md) - Virtual environment setup

## License

**Code**: All code in this repository is licensed under the GNU Affero General Public License v3.0 (AGPLv3). See the [LICENSE](LICENSE) file for details.

**Documentation and Other Content**: All non-code content (documentation, images, etc.) is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0). See the [LICENSE-CC-BY-SA](LICENSE-CC-BY-SA) file for details.

## Development Status

This project is in active development. See [PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for current status and roadmap.

