# SMCP IMAP/SMTP Plugins Project Plan

## Project Overview

This project aims to create comprehensive command-line tools for IMAP (email reading) and SMTP (email sending) that can be wrapped by UCW (Universal Command Wrapper) to become SMCP plugins. This approach simplifies development by building standard CLI tools that UCW can automatically convert into SMCP-compatible plugins, eliminating the need for full SMCP server integration during development and testing.

**Key Insight**: We don't need to build full SMCP plugins directly. Instead, we build well-structured CLI tools that UCW can wrap, making them instantly usable as SMCP plugins.

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

### Step 1.1: Analyze SMCP and UCW Requirements

**Objective**: Understand both SMCP plugin structure and UCW wrapping requirements.

**Tasks**:
- [x] Clone `sanctumos/smcp` repository into `tmp/smcp-analysis/`
- [x] Clone `actuallyrizzn/ucw` repository into `tmp/ucw-analysis/`
- [ ] Analyze existing SMCP plugin examples (botfather, devops):
  - CLI structure (argparse-based)
  - JSON output format
  - Command organization
  - Error handling patterns
- [ ] Analyze UCW wrapping requirements:
  - What UCW expects from CLI tools
  - How UCW generates SMCP plugins
  - JSON output requirements
  - Command structure expectations
- [ ] Document simplified development approach:
  - Build standard CLI tools (not full SMCP plugins)
  - UCW handles SMCP integration automatically
  - Focus on IMAP/SMTP functionality, not SMCP specifics

**Deliverable**: Documentation of UCW-compatible CLI tool requirements and simplified architecture

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
- [ ] Research DKIM behavior:
  - AOL's automatic DKIM signing
  - DNS requirements for custom domains
  - Verification methods

**Deliverable**: Technical specification for IMAP/SMTP implementation

### Step 1.2.5: Protocol-Level Failure Profiling

**Objective**: Map AOL's IMAP/SMTP behavior quirks and failure modes before plugin development.

**Tasks**:
- [ ] Test authentication failure scenarios:
  - Wrong credentials
  - Expired credentials
  - Rate limiting behavior
- [ ] Test connection behavior:
  - Too frequent connections
  - Concurrent connection limits
  - Timeout handling
- [ ] Test fetch operations:
  - Large message handling
  - Malformed MIME parsing
  - Header parsing edge cases
  - Attachment handling limits
- [ ] Test search operations:
  - Complex search queries
  - Date range edge cases
  - Invalid mailbox names
- [ ] Test SMTP behavior:
  - DKIM signing verification
  - Rate limiting
  - Large attachment handling
  - Invalid recipient handling
- [ ] Document all failure modes and error responses
- [ ] Create test corpus of malformed MIME samples

**Deliverable**: AOL-specific protocol behavior documentation and test corpus

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

### Step 2.1: IMAP CLI Tool Structure Setup

**Tasks**:
- [ ] Create `tools/imap/` directory structure (not `plugins/` - these are CLI tools, not SMCP plugins yet)
- [ ] Create `tools/imap/cli.py` (main CLI interface)
- [ ] Create `tools/imap/README.md` (documentation)
- [ ] Set up basic argparse structure following UCW-compatible patterns:
  - Standard argparse with subparsers for commands
  - JSON output for all commands (UCW/SMCP compatible)
  - Clear error handling with JSON error responses
  - Help text that UCW can parse

### Step 2.2: Core IMAP Functionality

**Tasks**:
- [ ] Implement connection management:
  - `connect` command (connect to IMAP server)
  - `disconnect` command
  - Connection pooling/reuse with thread-safety considerations
  - One connection per agent namespace OR queued request pattern
- [ ] Implement normalization layer:
  - Standard JSON schema for all email responses
  - Agent-friendly format (not raw IMAP wire protocol)
  - Consistent structure across all commands
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
- [ ] Implement email reading with guardrails:
  - `fetch` command (fetch email by UID)
  - `fetch-headers` command
  - `fetch-body` command (with `MAX_BODY_BYTES` truncation)
  - `fetch-attachments` command (with `MAX_ATTACHMENT_BYTES` limits)
  - `fetch-recent` command (fetch recent emails)
  - Malformed MIME handling and recovery
- [ ] Implement email management (with sandbox mode):
  - `mark-read` command (disabled in sandbox)
  - `mark-unread` command (disabled in sandbox)
  - `delete` command (disabled in sandbox)
  - `move` command (disabled in sandbox)
  - `copy` command
  - Sandbox mode flag to disable destructive operations

### Step 2.3: UCW Integration and Testing

**Tasks**:
- [ ] Test IMAP CLI tool with UCW wrapper:
  - Use UCW to wrap the IMAP CLI tool
  - Verify UCW can parse commands correctly
  - Test generated SMCP plugin functionality
- [ ] Verify JSON output format is UCW-compatible
- [ ] Test error handling produces valid JSON
- [ ] Add logging support (to stderr, not stdout - stdout is for JSON)
- [ ] Document UCW wrapping process

### Step 2.4: IMAP Plugin Testing

**Tasks**:
- [ ] Unit tests for each command
- [ ] Integration tests with AOL accounts
- [ ] Test error scenarios (invalid credentials, network issues)
- [ ] Test with various email formats (plain text, HTML, attachments)
- [ ] Performance testing (large mailboxes)

## Phase 3: SMTP Plugin Development

### Step 3.1: SMTP CLI Tool Structure Setup

**Tasks**:
- [ ] Create `tools/smtp/` directory structure (not `plugins/` - these are CLI tools)
- [ ] Create `tools/smtp/cli.py` (main CLI interface)
- [ ] Create `tools/smtp/README.md` (documentation)
- [ ] Set up basic argparse structure following UCW-compatible patterns:
  - Standard argparse with subparsers for commands
  - JSON output for all commands (UCW/SMCP compatible)
  - Clear error handling with JSON error responses
  - Help text that UCW can parse

### Step 3.2: Core SMTP Functionality

**Tasks**:
- [ ] Implement connection management:
  - `connect` command (connect to SMTP server)
  - `disconnect` command
  - Connection pooling/reuse with thread-safety
  - One connection per agent namespace OR queued request pattern
- [ ] Verify DKIM behavior:
  - Test AOL's automatic DKIM signing
  - Document DKIM verification process
  - Handle custom domain DKIM if needed
- [ ] Implement email sending with guardrails:
  - `send` command (send plain text email)
  - `send-html` command (send HTML email)
  - `send-with-attachment` command (with `MAX_ATTACHMENT_BYTES` limits)
  - Support for:
    - To, CC, BCC recipients
    - Subject line
    - Reply-To header
    - Custom headers
    - Multiple attachments
  - Rate limiting awareness
  - Large attachment handling
- [ ] Implement email composition helpers:
  - `compose` command (interactive composition)
  - Template support
  - Attachment handling with size validation

### Step 3.3: UCW Integration and Testing

**Tasks**:
- [ ] Test SMTP CLI tool with UCW wrapper:
  - Use UCW to wrap the SMTP CLI tool
  - Verify UCW can parse commands correctly
  - Test generated SMCP plugin functionality
- [ ] Verify JSON output format is UCW-compatible
- [ ] Test error handling produces valid JSON
- [ ] Add logging support (to stderr, not stdout - stdout is for JSON)
- [ ] Document UCW wrapping process

### Step 3.4: SMTP Plugin Testing

**Tasks**:
- [ ] Unit tests for each command
- [ ] Integration tests with AOL accounts (send between test accounts)
- [ ] Test error scenarios (invalid credentials, network issues, invalid recipients)
- [ ] Test with various email formats (plain text, HTML, attachments)
- [ ] Test with various attachment types and sizes

## Phase 4: Integration and Compatibility

### Step 4.1: UCW Wrapping and SMCP Integration

**Tasks**:
- [ ] Use UCW to generate SMCP plugins from both CLI tools:
  - Wrap IMAP CLI tool → SMCP plugin
  - Wrap SMTP CLI tool → SMCP plugin
- [ ] Test wrapped plugins with SanctumOS SMCP server
- [ ] Test wrapped plugins with Animus SMCP server (if available)
- [ ] Verify tool discovery and registration
- [ ] Test tool calls from AI agents
- [ ] Verify UCW-generated parameter schemas work correctly

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

### Step 5.1: Packaging and Distribution

**Tasks**:
- [ ] Create installation instructions:
  - How to use CLI tools directly
  - How to wrap with UCW for SMCP integration
  - How to deploy wrapped plugins to SMCP server
- [ ] Package CLI tools for distribution
- [ ] Create example UCW wrapping configurations
- [ ] Document the UCW wrapping workflow
- [ ] Prepare for repository submission

### Step 5.2: Final Testing

**Tasks**:
- [ ] End-to-end testing with real AI agents
- [ ] Performance testing under load
- [ ] Compatibility testing across platforms
- [ ] User acceptance testing

## Technical Specifications

### Normalization Layer Contract

All IMAP responses will be normalized to this agent-friendly JSON structure:

```json
{
  "id": "<uid>",
  "mailbox": "INBOX",
  "from": {
    "name": "Display Name",
    "email": "sender@example.com"
  },
  "to": [
    {
      "name": "Recipient Name",
      "email": "recipient@example.com"
    }
  ],
  "cc": [],
  "bcc": [],
  "subject": "Email Subject",
  "timestamp": "2025-12-02T11:00:00Z",
  "body": {
    "text": "Plain text body",
    "html": "<html>HTML body</html>",
    "attachments": [
      {
        "filename": "document.pdf",
        "content_type": "application/pdf",
        "size": 12345,
        "truncated": false
      }
    ]
  },
  "headers": {
    "message-id": "<message-id>",
    "references": [],
    "in-reply-to": null
  },
  "flags": ["seen", "answered"]
}
```

This structure becomes the lingua franca for agentic reasoning, abstracting away IMAP's wire protocol complexity.

### Concurrency Model

**Thread-Safety Considerations**:
- `imaplib` is NOT thread-safe by default
- Implement one of two patterns:
  1. **One connection per agent namespace**: Each agent gets its own IMAP connection
  2. **Queued request pattern**: Single connection with request queue for concurrent access
- Document chosen pattern and rationale
- Test concurrent fetch operations to ensure no data corruption

### Guardrails and Limits

**Configurable Limits**:
- `MAX_BODY_BYTES`: Maximum email body size (default: 10MB, configurable)
- `MAX_ATTACHMENT_BYTES`: Maximum attachment size (default: 25MB, configurable)
- `MAX_MESSAGES_PER_FETCH`: Maximum messages in single fetch (default: 100)
- Safe truncation logic for oversized content
- Clear indication when content is truncated

**Sandbox Mode**:
- Environment variable: `SMCP_IMAP_SANDBOX=true`
- When enabled, disables all destructive operations:
  - `delete` command
  - `move` command
  - `mark-read` / `mark-unread` commands
- Logs all would-be destructive operations for review
- Allows safe development and testing without risk

### Malformed MIME Handling

- Test corpus of intentionally chaotic MIME samples
- Robust parsing with graceful degradation
- Fallback to raw text when MIME parsing fails
- Log warnings for malformed emails
- Never crash on malformed input

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
2. **Protocol Failure Tests**: Test all AOL-specific failure modes identified in Phase 1.2.5
3. **Integration Tests**: Test with real IMAP/SMTP servers (AOL accounts)
4. **Concurrency Tests**: Test thread-safety and concurrent operations
5. **Malformed MIME Tests**: Test with chaotic MIME samples
6. **Guardrail Tests**: Test size limits and truncation behavior
7. **Sandbox Mode Tests**: Verify destructive operations are disabled
8. **SMCP Integration Tests**: Test plugin discovery and tool registration
9. **End-to-End Tests**: Test complete workflows (send email, read email)
10. **Error Handling Tests**: Test error scenarios and edge cases

## Security Considerations

1. **Credential Storage**: Never store credentials in code or logs
2. **Environment Variables**: Use environment variables for sensitive data
3. **TLS/SSL**: Always use encrypted connections
4. **Input Validation**: Validate all user inputs
5. **Rate Limiting**: Consider rate limiting for production use
6. **Error Messages**: Don't expose sensitive information in error messages

## Timeline Estimate

- **Phase 1**: 3-4 days (Analysis, test account setup, and protocol profiling)
- **Phase 2**: 6-8 days (IMAP plugin development with normalization layer)
- **Phase 3**: 6-8 days (SMTP plugin development with DKIM verification)
- **Phase 4**: 3-4 days (Integration, concurrency testing, and compatibility)
- **Phase 5**: 1-2 days (Deployment and distribution)

**Total Estimated Time**: 19-26 days

*Note: Additional time accounts for protocol profiling, normalization layer implementation, and comprehensive concurrency testing.*

## Success Criteria

1. ✅ Both plugins successfully discovered by SMCP server
2. ✅ All commands work correctly with AOL test accounts
3. ✅ Plugins compatible with both SanctumOS and Animus SMCP
4. ✅ Comprehensive documentation and examples
5. ✅ All tests passing
6. ✅ Security best practices implemented
7. ✅ Ready for production use

## Architecture Simplification: UCW-Based Approach

### Why UCW Simplifies Development

Instead of building full SMCP plugins directly, we build **standard CLI tools** that UCW can automatically wrap:

1. **Simpler Development**: Focus on IMAP/SMTP functionality, not SMCP integration
2. **Easier Testing**: Test CLI tools directly without SMCP server
3. **Automatic Integration**: UCW handles SMCP plugin generation
4. **Standard Patterns**: Use standard argparse, JSON output - no SMCP-specific code needed
5. **Flexibility**: CLI tools can be used standalone OR as SMCP plugins

### Development Workflow

1. **Build CLI Tools** (`tools/imap/cli.py`, `tools/smtp/cli.py`)
   - Standard argparse structure
   - JSON output for all commands
   - Error handling with JSON error responses

2. **Test with UCW**
   - Use UCW to wrap CLI tools
   - Verify UCW can parse and generate SMCP plugins
   - Test wrapped plugins with SMCP server

3. **Deploy**
   - Option A: Use UCW-wrapped plugins in SMCP
   - Option B: Use CLI tools directly (if needed)

### UCW Requirements

- **JSON Output**: All commands must output JSON (not plain text)
- **Standard argparse**: UCW can parse standard argparse help text
- **Error Handling**: Errors should be JSON objects with `{"error": "message"}` format
- **Help Text**: Clear help text that UCW can parse for command discovery

## Next Steps

1. ✅ Complete Phase 1.1: Analyze SMCP and UCW requirements (in progress)
2. Begin Phase 1.2.5: Protocol-level failure profiling with AOL accounts
3. Begin Phase 1.3: Create AOL test accounts
4. Begin Phase 2.1: Create IMAP CLI tool structure (UCW-compatible)
5. Test UCW wrapping early to validate approach

---

## Architecture Notes

### Why This Matters

This plugin provides **asynchronous external communication**—the ability for agents to:
- Receive tasks, signals, alerts, and documents via email
- Communicate with human intent through the world's most ubiquitous protocol
- Expand their reach beyond the immediate system boundaries

This becomes one of the "baseline sense organs" of SanctumOS—like vision, audio, memory, or motor control. It enables agents to participate in the broader digital ecosystem.

### Design Philosophy

- **Agent-First**: All responses normalized to agent-friendly JSON, not raw protocol
- **Safety-First**: Sandbox mode and guardrails prevent accidental destruction
- **Robustness-First**: Handle malformed input gracefully, never crash
- **Concurrency-Aware**: Thread-safe design for multi-agent environments
- **Protocol-Aware**: Understand server quirks before building abstractions

---

**Project Start Date**: December 2, 2025  
**Last Updated**: December 2, 2025  
**Status**: Planning Phase - Refined with architectural considerations

