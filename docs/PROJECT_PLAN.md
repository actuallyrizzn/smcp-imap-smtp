# SMCP IMAP/SMTP Plugins Project Plan

## Project Overview

This project aims to create comprehensive SMCP (Sanctum Model Context Protocol) plugins that enable AI agents to interact with email systems via IMAP (for reading emails) and SMTP (for sending emails). These plugins will be compatible with both Animus and SanctumOS flavors of SMCP, with primary focus on SanctumOS deployment.

## Project Goals

1. **IMAP Plugin**: Full-featured email reading capabilities
   - Connect to IMAP servers
   - List mailboxes/folders
   - Search and filter emails
   - Read email content (headers, body, attachments)
   - Mark emails as read/unread
   - Delete emails
   - Move emails between folders

2. **SMTP Plugin**: Full-featured email sending capabilities
   - Connect to SMTP servers
   - Send plain text emails
   - Send HTML emails
   - Send emails with attachments
   - Support CC, BCC, Reply-To headers
   - Handle authentication (TLS/SSL)

3. **Compatibility**: Ensure plugins work with both Animus and SanctumOS SMCP implementations

## Phase 1: Analysis and Planning

### Step 1.1: Clone and Analyze SMCP Structure

**Objective**: Understand the SMCP plugin architecture and interface requirements.

**Tasks**:
- [ ] Clone `sanctumos/smcp` repository into `tmp/smcp-analysis/`
- [ ] Analyze existing plugin examples (botfather, devops)
- [ ] Document plugin structure requirements:
  - Directory structure
  - CLI interface requirements
  - `--describe` command format
  - Parameter schema requirements
  - Error handling patterns
  - Output format (JSON)
- [ ] Review plugin discovery mechanism
- [ ] Understand tool registration process

**Deliverable**: Documentation of SMCP plugin architecture and requirements

### Step 1.2: Research Email Protocol Requirements

**Objective**: Understand IMAP and SMTP protocol requirements and Python libraries.

**Tasks**:
- [ ] Research Python IMAP libraries:
  - `imaplib` (standard library)
  - `imapclient` (third-party, more feature-rich)
- [ ] Research Python SMTP libraries:
  - `smtplib` (standard library)
  - `aiosmtplib` (async alternative)
- [ ] Document common email server configurations:
  - Gmail (IMAP/SMTP settings)
  - Outlook/Office365
  - Yahoo
  - AOL (for testing)
  - Generic IMAP/SMTP servers
- [ ] Research security requirements:
  - OAuth2 authentication
  - App passwords
  - TLS/SSL requirements
  - Two-factor authentication considerations

**Deliverable**: Technical specification for IMAP/SMTP implementation

### Step 1.3: Create Test Accounts

**Objective**: Set up AOL email accounts for testing purposes.

**Tasks**:
- [ ] Navigate to AOL account creation page
- [ ] Create first AOL test account:
  - Username: `smcptest1@aol.com` (or available variant)
  - Secure password
  - Recovery information
- [ ] Create second AOL test account:
  - Username: `smcptest2@aol.com` (or available variant)
  - Secure password
  - Recovery information
- [ ] Document account credentials securely
- [ ] Test IMAP/SMTP connectivity with both accounts
- [ ] Document AOL IMAP/SMTP server settings:
  - IMAP server: `imap.aol.com`
  - IMAP port: `993` (SSL)
  - SMTP server: `smtp.aol.com`
  - SMTP port: `587` (TLS) or `465` (SSL)
- [ ] Verify account functionality (send/receive test emails)

**Deliverable**: Two functional AOL test accounts with documented settings

## Phase 2: IMAP Plugin Development

### Step 2.1: Plugin Structure Setup

**Tasks**:
- [ ] Create `plugins/imap/` directory structure
- [ ] Create `plugins/imap/__init__.py`
- [ ] Create `plugins/imap/cli.py` (main plugin interface)
- [ ] Create `plugins/imap/README.md` (documentation)
- [ ] Set up basic CLI argument parser structure

### Step 2.2: Core IMAP Functionality

**Tasks**:
- [ ] Implement connection management:
  - `connect` command (connect to IMAP server)
  - `disconnect` command
  - Connection pooling/reuse
- [ ] Implement mailbox operations:
  - `list-mailboxes` command (list all folders)
  - `select-mailbox` command (select a mailbox)
  - `create-mailbox` command
  - `delete-mailbox` command
- [ ] Implement email search:
  - `search` command (search by criteria)
  - `search-unread` command
  - `search-by-sender` command
  - `search-by-subject` command
  - `search-by-date` command
- [ ] Implement email reading:
  - `fetch` command (fetch email by UID)
  - `fetch-headers` command
  - `fetch-body` command
  - `fetch-attachments` command
  - `fetch-recent` command (fetch recent emails)
- [ ] Implement email management:
  - `mark-read` command
  - `mark-unread` command
  - `delete` command
  - `move` command (move to folder)
  - `copy` command

### Step 2.3: IMAP Plugin Integration

**Tasks**:
- [ ] Implement `--describe` command with full parameter schemas
- [ ] Define JSON schema for all commands
- [ ] Implement error handling and user-friendly error messages
- [ ] Add logging support
- [ ] Test plugin discovery by SMCP server
- [ ] Verify tool registration

### Step 2.4: IMAP Plugin Testing

**Tasks**:
- [ ] Unit tests for each command
- [ ] Integration tests with AOL accounts
- [ ] Test error scenarios (invalid credentials, network issues)
- [ ] Test with various email formats (plain text, HTML, attachments)
- [ ] Performance testing (large mailboxes)

## Phase 3: SMTP Plugin Development

### Step 3.1: Plugin Structure Setup

**Tasks**:
- [ ] Create `plugins/smtp/` directory structure
- [ ] Create `plugins/smtp/__init__.py`
- [ ] Create `plugins/smtp/cli.py` (main plugin interface)
- [ ] Create `plugins/smtp/README.md` (documentation)
- [ ] Set up basic CLI argument parser structure

### Step 3.2: Core SMTP Functionality

**Tasks**:
- [ ] Implement connection management:
  - `connect` command (connect to SMTP server)
  - `disconnect` command
  - Connection pooling/reuse
- [ ] Implement email sending:
  - `send` command (send plain text email)
  - `send-html` command (send HTML email)
  - `send-with-attachment` command
  - Support for:
    - To, CC, BCC recipients
    - Subject line
    - Reply-To header
    - Custom headers
    - Multiple attachments
- [ ] Implement email composition helpers:
  - `compose` command (interactive composition)
  - Template support
  - Attachment handling

### Step 3.3: SMTP Plugin Integration

**Tasks**:
- [ ] Implement `--describe` command with full parameter schemas
- [ ] Define JSON schema for all commands
- [ ] Implement error handling and user-friendly error messages
- [ ] Add logging support
- [ ] Test plugin discovery by SMCP server
- [ ] Verify tool registration

### Step 3.4: SMTP Plugin Testing

**Tasks**:
- [ ] Unit tests for each command
- [ ] Integration tests with AOL accounts (send between test accounts)
- [ ] Test error scenarios (invalid credentials, network issues, invalid recipients)
- [ ] Test with various email formats (plain text, HTML, attachments)
- [ ] Test with various attachment types and sizes

## Phase 4: Integration and Compatibility

### Step 4.1: SMCP Integration Testing

**Tasks**:
- [ ] Test plugins with SanctumOS SMCP server
- [ ] Test plugins with Animus SMCP server (if available)
- [ ] Verify tool discovery and registration
- [ ] Test tool calls from AI agents
- [ ] Verify parameter schema validation

### Step 4.2: Documentation

**Tasks**:
- [ ] Complete plugin README files
- [ ] Create usage examples
- [ ] Document configuration requirements
- [ ] Create troubleshooting guide
- [ ] Document security considerations

### Step 4.3: Security Hardening

**Tasks**:
- [ ] Implement secure credential storage (environment variables)
- [ ] Add input validation
- [ ] Implement rate limiting considerations
- [ ] Document security best practices
- [ ] Add credential masking in logs

## Phase 5: Deployment and Distribution

### Step 5.1: Packaging

**Tasks**:
- [ ] Create installation instructions
- [ ] Package plugins for distribution
- [ ] Create example configurations
- [ ] Prepare for repository submission

### Step 5.2: Final Testing

**Tasks**:
- [ ] End-to-end testing with real AI agents
- [ ] Performance testing under load
- [ ] Compatibility testing across platforms
- [ ] User acceptance testing

## Technical Specifications

### IMAP Plugin Commands

1. **connect**
   - Parameters: `server`, `port`, `username`, `password`, `use_ssl`
   - Returns: Connection status

2. **list-mailboxes**
   - Parameters: None (uses active connection)
   - Returns: List of mailboxes with metadata

3. **select-mailbox**
   - Parameters: `mailbox_name`
   - Returns: Mailbox status (message count, etc.)

4. **search**
   - Parameters: `criteria` (JSON object with search criteria)
   - Returns: List of email UIDs matching criteria

5. **fetch**
   - Parameters: `uid`, `parts` (headers, body, attachments)
   - Returns: Email content in structured format

6. **mark-read / mark-unread**
   - Parameters: `uid` or `uids` (array)
   - Returns: Operation status

7. **delete**
   - Parameters: `uid` or `uids` (array)
   - Returns: Operation status

8. **move**
   - Parameters: `uid`, `target_mailbox`
   - Returns: Operation status

### SMTP Plugin Commands

1. **connect**
   - Parameters: `server`, `port`, `username`, `password`, `use_tls`
   - Returns: Connection status

2. **send**
   - Parameters: `to`, `subject`, `body`, `from`, `cc` (optional), `bcc` (optional), `reply_to` (optional)
   - Returns: Send status and message ID

3. **send-html**
   - Parameters: `to`, `subject`, `html_body`, `text_body` (optional), `from`, `cc` (optional), `bcc` (optional)
   - Returns: Send status and message ID

4. **send-with-attachment**
   - Parameters: `to`, `subject`, `body`, `from`, `attachments` (array of file paths), `cc` (optional), `bcc` (optional)
   - Returns: Send status and message ID

## Dependencies

### Python Libraries
- `imaplib` (standard library) or `imapclient` (recommended)
- `smtplib` (standard library) or `aiosmtplib` (for async)
- `email` (standard library) for email parsing/construction
- `argparse` (standard library) for CLI
- `json` (standard library) for output formatting

### Optional
- `python-dotenv` for environment variable management
- `cryptography` for advanced security features

## Testing Strategy

1. **Unit Tests**: Test individual command functions
2. **Integration Tests**: Test with real IMAP/SMTP servers (AOL accounts)
3. **SMCP Integration Tests**: Test plugin discovery and tool registration
4. **End-to-End Tests**: Test complete workflows (send email, read email)
5. **Error Handling Tests**: Test error scenarios and edge cases

## Security Considerations

1. **Credential Storage**: Never store credentials in code or logs
2. **Environment Variables**: Use environment variables for sensitive data
3. **TLS/SSL**: Always use encrypted connections
4. **Input Validation**: Validate all user inputs
5. **Rate Limiting**: Consider rate limiting for production use
6. **Error Messages**: Don't expose sensitive information in error messages

## Timeline Estimate

- **Phase 1**: 2-3 days (Analysis and test account setup)
- **Phase 2**: 5-7 days (IMAP plugin development)
- **Phase 3**: 5-7 days (SMTP plugin development)
- **Phase 4**: 2-3 days (Integration and compatibility)
- **Phase 5**: 1-2 days (Deployment and distribution)

**Total Estimated Time**: 15-22 days

## Success Criteria

1. ✅ Both plugins successfully discovered by SMCP server
2. ✅ All commands work correctly with AOL test accounts
3. ✅ Plugins compatible with both SanctumOS and Animus SMCP
4. ✅ Comprehensive documentation and examples
5. ✅ All tests passing
6. ✅ Security best practices implemented
7. ✅ Ready for production use

## Next Steps

1. Begin Phase 1.1: Clone SMCP repository for analysis
2. Begin Phase 1.3: Create AOL test accounts
3. Review and refine this plan based on SMCP structure analysis

---

**Project Start Date**: December 2, 2025  
**Last Updated**: December 2, 2025  
**Status**: Planning Phase

