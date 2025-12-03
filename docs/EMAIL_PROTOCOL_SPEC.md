# Email Protocol Implementation Specification

## Overview

This document specifies the technical requirements for implementing IMAP and SMTP functionality in Python, including library choices, server configurations, and security considerations.

## Python Library Selection

### IMAP Libraries

#### Option 1: `imaplib` (Standard Library)
- **Pros**: 
  - No external dependencies
  - Always available
  - Part of Python standard library
- **Cons**:
  - Lower-level API
  - More verbose code
  - Less convenient for common operations
- **Verdict**: Use as fallback, but prefer `imapclient` for better developer experience

#### Option 2: `imapclient` (Third-Party, Recommended)
- **Pros**:
  - Higher-level, more Pythonic API
  - Better error handling
  - Easier to work with
  - Active maintenance
  - Better documentation
- **Cons**:
  - External dependency (but lightweight)
- **Verdict**: **RECOMMENDED** - Better developer experience, worth the dependency

**Decision**: Use `imapclient` as primary library, with `imaplib` as fallback if needed.

### SMTP Libraries

#### Option 1: `smtplib` (Standard Library)
- **Pros**:
  - No external dependencies
  - Always available
  - Sufficient for our needs
- **Cons**:
  - Synchronous only (but that's fine for CLI tools)
- **Verdict**: **USE THIS** - Standard library is sufficient for SMTP

#### Option 2: `aiosmtplib` (Async Alternative)
- **Pros**:
  - Async support
- **Cons**:
  - Not needed for CLI tools (CLI is inherently synchronous)
  - Adds unnecessary complexity
- **Verdict**: **SKIP** - Not needed for CLI tools

**Decision**: Use `smtplib` (standard library) for SMTP.

### Email Parsing/Construction

#### `email` (Standard Library)
- **Pros**:
  - Always available
  - Comprehensive MIME support
  - Well-tested
- **Verdict**: **USE THIS** - Standard library is perfect for email parsing/construction

## Email Server Configurations

### AOL (Primary Testing Target)

**IMAP Settings**:
- Server: `imap.aol.com`
- Port: `993` (SSL/TLS)
- Security: SSL/TLS required
- Authentication: Username/password (or app password)

**SMTP Settings**:
- Server: `smtp.aol.com`
- Port: `587` (STARTTLS) or `465` (SSL)
- Security: TLS/SSL required
- Authentication: Username/password (or app password)

**Notes**:
- AOL requires SSL/TLS for both IMAP and SMTP
- May require app password if 2FA is enabled
- DKIM signing: AOL automatically signs outbound mail (verify during testing)

### Gmail (Reference)

**IMAP Settings**:
- Server: `imap.gmail.com`
- Port: `993` (SSL/TLS)
- Security: SSL/TLS required
- Authentication: OAuth2 or app password

**SMTP Settings**:
- Server: `smtp.gmail.com`
- Port: `587` (STARTTLS) or `465` (SSL)
- Security: TLS/SSL required
- Authentication: OAuth2 or app password

**Notes**:
- Gmail requires app passwords for non-OAuth2 access
- OAuth2 is more complex but more secure
- For initial implementation, focus on app passwords

### Outlook/Office365 (Reference)

**IMAP Settings**:
- Server: `outlook.office365.com`
- Port: `993` (SSL/TLS)
- Security: SSL/TLS required
- Authentication: OAuth2 or app password

**SMTP Settings**:
- Server: `smtp.office365.com`
- Port: `587` (STARTTLS)
- Security: TLS/SSL required
- Authentication: OAuth2 or app password

### Yahoo (Reference)

**IMAP Settings**:
- Server: `imap.mail.yahoo.com`
- Port: `993` (SSL/TLS)
- Security: SSL/TLS required
- Authentication: App password required

**SMTP Settings**:
- Server: `smtp.mail.yahoo.com`
- Port: `587` (STARTTLS) or `465` (SSL)
- Security: TLS/SSL required
- Authentication: App password required

### Generic IMAP/SMTP Servers

**IMAP Settings**:
- Server: Configurable
- Port: `993` (SSL/TLS) or `143` (STARTTLS)
- Security: SSL/TLS or STARTTLS
- Authentication: Username/password

**SMTP Settings**:
- Server: Configurable
- Port: `587` (STARTTLS) or `465` (SSL) or `25` (unencrypted, not recommended)
- Security: TLS/SSL or STARTTLS
- Authentication: Username/password

## Security Requirements

### Authentication Methods

1. **Username/Password** (Basic)
   - Simple but less secure
   - Works with most servers
   - Use for initial implementation

2. **App Passwords** (Recommended for production)
   - More secure than regular passwords
   - Required by Gmail, Yahoo
   - Recommended for AOL

3. **OAuth2** (Future enhancement)
   - Most secure
   - Complex to implement
   - Defer to future phase

### TLS/SSL Requirements

- **Always use encrypted connections** for IMAP and SMTP
- **Prefer SSL/TLS** (port 993 for IMAP, 465 for SMTP) over STARTTLS
- **Never use unencrypted** connections (port 25 without encryption)
- **Validate certificates** (Python's ssl module handles this by default)

### Two-Factor Authentication (2FA)

- Many providers require app passwords when 2FA is enabled
- Document this requirement in user documentation
- Provide clear error messages when 2FA is blocking access

## DKIM Behavior

### AOL DKIM Signing

- **Automatic**: AOL automatically DKIM-signs all outbound mail
- **No DNS configuration needed**: For AOL accounts
- **Verification**: Test during Phase 1.2.5 to confirm behavior
- **Custom domains**: If using custom domains with AOL, DNS configuration may be required

### DKIM Verification

- Verify DKIM signatures on received emails (optional, for future)
- Document DKIM status in email headers (if present)
- Not critical for initial implementation, but good to verify

## Implementation Priorities

### Phase 1 (Initial Implementation)
1. ✅ Use `imapclient` for IMAP
2. ✅ Use `smtplib` for SMTP
3. ✅ Use `email` for parsing/construction
4. ✅ Support username/password authentication
5. ✅ Support SSL/TLS connections
6. ✅ Focus on AOL for testing

### Phase 2 (Enhancements)
1. App password support (documentation)
2. OAuth2 support (future)
3. DKIM verification (optional)
4. Support for more providers

## Dependencies

### Required
- `imapclient` - IMAP client library
- Python standard library: `smtplib`, `email`, `ssl`, `json`, `argparse`

### Optional
- `python-dotenv` - Environment variable management (for credentials)

## Error Handling

### Common IMAP Errors
- Authentication failures
- Connection timeouts
- SSL/TLS errors
- Server errors (IMAP protocol errors)
- Network errors

### Common SMTP Errors
- Authentication failures
- Connection timeouts
- SSL/TLS errors
- Invalid recipient addresses
- Server rejections (spam, rate limiting)
- Attachment size limits

### Error Response Format
All errors should be JSON:
```json
{
  "error": "Error message",
  "error_type": "authentication|connection|protocol|network",
  "details": "Additional error details if available"
}
```

## Testing Strategy

### Test Accounts
- Two AOL accounts (primary testing)
- Optional: Gmail, Outlook accounts for compatibility testing

### Test Scenarios
1. Successful connections
2. Authentication failures
3. Network timeouts
4. Invalid server settings
5. Large attachments
6. Malformed emails
7. Rate limiting

---

**Document Status**: Initial specification complete  
**Last Updated**: December 2, 2025  
**Next**: Phase 1.2.5 - Protocol-level failure profiling with AOL accounts

