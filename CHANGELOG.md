# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Account profile management system (`tools/profile_cli.py`)
- `--account` flag support in IMAP/SMTP commands
- Comprehensive test suite (33 tests covering IMAP, SMTP, MIME edge cases, concurrency, integration)
- Malformed MIME test corpus (`tests/malformed_mime/`)
- Protocol failure profiling documentation (`docs/PROTOCOL_FAILURE_PROFILING.md`)
- Concurrency documentation (`docs/CONCURRENCY.md`)
- Sandbox mode examples in README
- `imapclient` library rationale in README

### Changed
- Updated README with account profile usage examples
- Improved error messages for authentication failures
- Auto-connect now supports account profiles and default profiles

### Fixed
- Fixed JSON serialization for IMAP `list-mailboxes` (bytes to string conversion)
- Fixed auto-selection of INBOX for search/fetch operations
- Fixed auto-selection of INBOX for mark-read/unread/delete/move operations

## [0.1.0] - 2025-12-03

### Added
- Initial release
- IMAP CLI tool with full email reading capabilities
- SMTP CLI tool with email sending capabilities
- Email normalization layer for agent-friendly JSON output
- Guardrails: MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES
- Sandbox mode for destructive operations
- Auto-connect functionality for all commands
- UCW compatibility (JSON output, argparse structure)
- Comprehensive documentation:
  - Project plan
  - Installation guide
  - Usage examples
  - Configuration guide
  - Troubleshooting guide
  - UCW requirements
  - Email protocol specifications
- Support for GMX and AOL email providers
- Malformed MIME handling with graceful degradation
- Protocol-level failure profiling

### Features

#### IMAP Tool
- Connect/disconnect to IMAP servers
- List and select mailboxes
- Search emails with various criteria
- Fetch email content with normalization
- Mark emails as read/unread
- Delete and move emails (with sandbox mode)
- Auto-connect with credentials or account profiles
- Auto-select INBOX when needed

#### SMTP Tool
- Connect/disconnect to SMTP servers
- Send plain text emails
- Send HTML emails
- Send emails with attachments
- Support for CC, BCC, Reply-To headers
- Auto-connect with credentials or account profiles

#### Account Profiles
- Named account profiles stored in `~/.smcp-imap-smtp/accounts.json`
- Profile management CLI (`tools/profile_cli.py`)
- Default profile support
- Secure credential storage (passwords stored in plain text - encryption recommended for production)

---

## Version History

- **0.1.0** (2025-12-03): Initial release with full IMAP/SMTP functionality

---

**Note:** This project follows semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

