# SMCP IMAP/SMTP Tools

Command-line tools for IMAP (email reading) and SMTP (email sending) that can be used standalone or wrapped by UCW (Universal Command Wrapper) to become SMCP plugins for AI agents.

## Overview

This project provides two CLI tools:
- **IMAP Tool**: Full-featured email reading capabilities
- **SMTP Tool**: Full-featured email sending capabilities

**Two Usage Modes:**
1. **Standalone**: Use directly from command line for testing and scripting
2. **SMCP Plugins**: Wrap with UCW and install in SMCP server for AI agent use

Both tools are designed to be UCW-compatible, making them instantly usable as SMCP plugins when wrapped.

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

## Usage Modes

This project can be used in two ways:

### 1. Standalone CLI Tools

Use the tools directly from the command line for testing, scripting, or manual operations.

### 2. SMCP Plugins (Recommended for Production)

Wrap the tools with UCW and install them as SMCP plugins for use by AI agents.

---

## Usage

### Mode 1: Standalone CLI Tools

#### IMAP Tool

**Using Account Profiles (Recommended):**
```bash
# Add an account profile
python tools/profile_cli.py add --name gmx --imap-server imap.gmx.com --smtp-server mail.gmx.com --username test@gmx.com --password pass

# Set as default profile
python tools/profile_cli.py set-default --name gmx

# Use profile for operations (uses default if no --account specified)
python tools/imap/cli.py list-mailboxes --account gmx
python tools/imap/cli.py search --criteria "ALL" --account gmx
python tools/imap/cli.py fetch --message-id 12345 --account gmx
```

**Using Direct Credentials:**
```bash
# Connect to IMAP server (auto-connects if credentials provided)
python tools/imap/cli.py list-mailboxes --server imap.gmx.com --username test@gmx.com --password pass

# Search emails (auto-connects and selects INBOX)
python tools/imap/cli.py search --criteria "ALL" --server imap.gmx.com --username test@gmx.com --password pass

# Fetch email
python tools/imap/cli.py fetch --message-id 12345 --server imap.gmx.com --username test@gmx.com --password pass

# Delete email in sandbox mode (simulates without actually deleting)
python tools/imap/cli.py delete --message-ids 12345 --sandbox --server imap.gmx.com --username test@gmx.com --password pass

# Delete email for real (no --sandbox flag)
python tools/imap/cli.py delete --message-ids 12345 --server imap.gmx.com --username test@gmx.com --password pass
```

#### SMTP Tool

**Using Account Profiles (Recommended):**
```bash
# Use profile for sending (uses default if no --account specified)
python tools/smtp/cli.py send --to recipient@example.com --subject "Test" --body "Hello" --account gmx
python tools/smtp/cli.py send-html --to recipient@example.com --subject "Test" --html "<html><body>Hello</body></html>" --account gmx
python tools/smtp/cli.py send-with-attachment --to recipient@example.com --subject "Test" --body "Hello" --attachments file.pdf --account gmx
```

**Using Direct Credentials:**
```bash
# Send email (auto-connects if credentials provided)
python tools/smtp/cli.py send --to recipient@example.com --subject "Test" --body "Hello" --server mail.gmx.com --username test@gmx.com --password pass

# Send HTML email
python tools/smtp/cli.py send-html --to recipient@example.com --subject "Test" --html "<html><body>Hello</body></html>" --server mail.gmx.com --username test@gmx.com --password pass

# Send email with attachment
python tools/smtp/cli.py send-with-attachment --to recipient@example.com --subject "Test" --body "Hello" --attachments file.pdf --server mail.gmx.com --username test@gmx.com --password pass
```

### Mode 2: SMCP Plugins (Recommended)

For production use with SMCP servers and AI agents, wrap the tools with UCW and install them as plugins.

#### Step 1: Wrap Tools with UCW

```bash
# Wrap IMAP tool
python ucw/cli.py wrap tools/imap/cli.py --output plugins/imap/cli.py

# Wrap SMTP tool
python ucw/cli.py wrap tools/smtp/cli.py --output plugins/smtp/cli.py
```

#### Step 2: Install in SMCP Server

Copy the wrapped plugins to your SMCP server's plugin directory:

```bash
# For SanctumOS SMCP
cp plugins/imap/cli.py /path/to/sanctumos-smcp/plugins/imap/
cp plugins/smtp/cli.py /path/to/sanctumos-smcp/plugins/smtp/

# For Animus SMCP
cp plugins/imap/cli.py /path/to/animus-smcp/plugins/imap/
cp plugins/smtp/cli.py /path/to/animus-smcp/plugins/smtp/
```

#### Step 3: Restart SMCP Server

The SMCP server will automatically discover the plugins and register them as available tools. AI agents can then use them via the SMCP protocol.

#### Plugin Usage in SMCP

Once installed, agents can call the tools through SMCP:

- **IMAP Tools**: `imap_list_mailboxes`, `imap_search`, `imap_fetch`, `imap_send`, etc.
- **SMTP Tools**: `smtp_send`, `smtp_send_html`, `smtp_send_with_attachment`

The SMCP server handles authentication, parameter passing, and response formatting automatically.

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
- Connect to IMAP servers (using `imapclient` library for robust MIME handling)
- List and select mailboxes
- Search emails
- Fetch email content with normalization
- Mark emails as read/unread
- Delete and move emails (with sandbox mode)
- Guardrails: MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES
- Auto-connect: Commands automatically connect if credentials provided
- Sandbox mode: `--sandbox` flag prevents destructive operations

### SMTP Tool
- Connect to SMTP servers
- Send plain text emails
- Send HTML emails
- Send emails with attachments
- Support for CC, BCC, Reply-To headers
- Guardrails: MAX_ATTACHMENT_BYTES
- Auto-connect: Commands automatically connect if credentials provided

### Why `imapclient` instead of `imaplib`?
We use `imapclient` (not the standard library `imaplib`) because:
- **Better MIME handling**: More robust parsing of malformed emails
- **Improved error messages**: Clearer error reporting for debugging
- **Better Unicode support**: Handles encoding issues more gracefully
- **Active maintenance**: Regularly updated with bug fixes and improvements

## Related Projects

- **[LettaAI](https://github.com/letta-ai/letta)** - LettaAI, the AI agent framework that SMCP is built for (though SMCP is not exclusively for LettaAI)
- **[SMCP (SanctumOS)](https://github.com/sanctumos/smcp)** - SanctumOS Model Context Protocol server
- **[SMCP (Animus)](https://github.com/AnimusUNO/smcp)** - Animus Model Context Protocol server
- **[UCW (Universal Command Wrapper)](https://github.com/actuallyrizzn/ucw)** - Universal Command Wrapper for wrapping CLI tools into SMCP plugins

## Documentation

- [Project Plan](docs/PROJECT_PLAN.md) - Detailed development plan
- [Installation Guide](docs/INSTALLATION.md) - Installation and setup instructions
- [Usage Examples](docs/USAGE_EXAMPLES.md) - Detailed usage examples
- [Configuration Guide](docs/CONFIGURATION.md) - Server configurations and settings
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [Concurrency Guide](docs/CONCURRENCY.md) - Concurrency model and rate limiting
- [UCW Requirements](docs/UCW_REQUIREMENTS.md) - UCW compatibility requirements
- [Email Protocol Spec](docs/EMAIL_PROTOCOL_SPEC.md) - Technical specifications
- [Protocol Failure Profiling](docs/PROTOCOL_FAILURE_PROFILING.md) - Failure modes and error handling
- [Setup Instructions](SETUP.md) - Virtual environment setup
- [Changelog](CHANGELOG.md) - Version history and changes

## License

**Code**: All code in this repository is licensed under the GNU Affero General Public License v3.0 (AGPLv3). See the [LICENSE](LICENSE) file for details.

**Documentation and Other Content**: All non-code content (documentation, images, etc.) is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0). See the [LICENSE-CC-BY-SA](LICENSE-CC-BY-SA) file for details.

## Development Status

This project is in active development. See [PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for current status and roadmap.

