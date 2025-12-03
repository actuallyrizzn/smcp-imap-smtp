# Protocol-Level Failure Profiling

This document profiles IMAP/SMTP failure modes, server quirks, and error handling requirements based on testing with GMX (primary) and AOL (reference).

## GMX (Primary Testing)

### Authentication Failure Scenarios

#### Wrong Credentials
- **Error**: `b'authentication failed'`
- **Behavior**: Immediate failure, no retry delay
- **Rate Limiting**: Multiple failed attempts may temporarily lock account (15-30 minute wait)
- **Recovery**: Wait period or log in via web to unlock

#### Missing IMAP Activation
- **Error**: `b'authentication failed'` (same as wrong credentials)
- **Behavior**: Authentication fails even with correct credentials if IMAP not enabled
- **Solution**: Enable IMAP in Settings > POP3 & IMAP
- **Activation Delay**: 5-15 minutes for IMAP to activate after enabling

#### 2FA Requirements
- **Behavior**: App-specific passwords required when 2FA is enabled
- **Error**: `b'authentication failed'` if using regular password with 2FA enabled
- **Solution**: Generate app-specific password from Security Options
- **Note**: 2FA must be enabled before app-specific passwords work

#### Expired/Invalid App Passwords
- **Error**: `b'authentication failed'`
- **Behavior**: Same as wrong credentials
- **Recovery**: Generate new app-specific password

### Connection Behavior

#### Too Frequent Connections
- **Test**: Multiple rapid connections
- **Result**: No observed rate limiting on connection attempts
- **Note**: GMX allows normal connection patterns

#### Concurrent Connection Limits
- **Test**: Multiple simultaneous connections
- **Result**: Standard IMAP allows one active connection per account
- **Behavior**: New connection may disconnect previous one
- **Recommendation**: Use connection pooling or single connection per agent namespace

#### Timeout Handling
- **Default Timeout**: 30 seconds
- **Behavior**: Connection hangs on network issues
- **Error**: `Connection timeout` or `Connection unexpectedly closed`
- **Recovery**: Retry with exponential backoff

#### SSL/TLS Certificate Issues
- **Behavior**: `imapclient` validates certificates by default
- **Error**: SSL certificate verification errors
- **Solution**: Use proper SSL context (default works for GMX)

### Fetch Operations

#### Large Message Handling
- **Guardrail**: `MAX_BODY_BYTES` (10MB default)
- **Behavior**: Body truncated if exceeds limit
- **Response**: `truncated: true` flag in normalized output
- **Attachment Limit**: `MAX_ATTACHMENT_BYTES` (25MB default)

#### Malformed MIME Parsing
- **Test**: Emails with corrupted headers, missing boundaries, invalid encoding
- **Behavior**: `email.message_from_bytes` handles gracefully
- **Fallback**: Partial parsing, missing fields return empty/default values
- **Error Handling**: Never crashes, returns partial data

#### Header Parsing Edge Cases
- **Missing Headers**: Returns `None` or empty string
- **Invalid Date Formats**: Uses fallback or current timestamp
- **Malformed Addresses**: Parses what it can, ignores invalid parts
- **Encoding Issues**: UTF-8 with errors='replace' handles most cases

#### Attachment Handling Limits
- **Size Limit**: 25MB default (configurable)
- **Behavior**: Attachment truncated if exceeds limit
- **Response**: `truncated: true` in attachment metadata
- **Large Attachments**: May cause memory issues if not truncated

### Search Operations

#### Complex Search Queries
- **Supported**: Standard IMAP search criteria
- **Examples**: `ALL`, `UNSEEN`, `FROM sender@example.com`, `SUBJECT "text"`
- **Behavior**: GMX supports standard IMAP search syntax
- **Error**: Invalid syntax returns empty results or protocol error

#### Date Range Edge Cases
- **Format**: IMAP date format required
- **Behavior**: Invalid dates cause search to fail
- **Error**: Protocol error or empty results

#### Invalid Mailbox Names
- **Error**: `select failed: unknown folder`
- **Behavior**: Immediate failure with clear error message
- **Recovery**: Use `list-mailboxes` to get valid mailbox names

#### Mailbox Selection Required
- **Error**: `SEARCH failed: [CLIENTBUG] please select mailbox first`
- **Behavior**: Search/fetch operations require mailbox selection
- **Solution**: Auto-select INBOX if no mailbox selected (implemented)

### SMTP Behavior

#### DKIM Signing Verification
- **GMX**: Automatically signs outbound mail with DKIM
- **Verification**: DKIM signature present in sent email headers
- **Behavior**: No manual DKIM setup required
- **Note**: AOL also automatically signs outbound mail

#### Rate Limiting
- **Test**: Multiple rapid sends
- **Result**: No observed rate limiting in testing
- **Note**: Production use should implement rate limiting

#### Large Attachment Handling
- **Limit**: 25MB default (configurable)
- **Behavior**: Attachment truncated if exceeds limit
- **Error**: May fail if server rejects large attachments
- **Recovery**: Split large attachments or use alternative delivery

#### Invalid Recipient Handling
- **Error**: SMTP server rejects invalid addresses
- **Behavior**: `send_email` raises exception
- **Error Types**: `SMTPRecipientsRefused`, `SMTPDataError`
- **Recovery**: Validate addresses before sending

#### Connection Issues
- **Port 587 (STARTTLS)**: Preferred, works reliably
- **Port 465 (SSL)**: Alternative, also works
- **Timeout**: 30 seconds default
- **Error**: `Connection unexpectedly closed` on network issues

## AOL (Reference/Backup)

### Authentication Requirements
- **App Passwords**: Required for IMAP/SMTP (cannot use regular password)
- **Generation**: Account Security page
- **Behavior**: Similar to GMX with 2FA enabled

### Server Settings
- **IMAP**: `imap.aol.com:993` (SSL)
- **SMTP**: `smtp.aol.com:587` (STARTTLS) or `465` (SSL)
- **DKIM**: Automatically signs outbound mail

### Known Quirks
- **App Password Only**: Cannot use regular password for IMAP/SMTP
- **Account Lock**: Multiple failed attempts may lock account temporarily

## Error Response Patterns

### IMAP Errors
```json
{
  "error": "Connection failed: Authentication failed. This may be due to:\n1. Incorrect username or password\n2. IMAP access may not be enabled in account settings\n3. App password may be incorrect or expired\n4. Account may need additional security setup\nOriginal error: b'authentication failed'"
}
```

### SMTP Errors
```json
{
  "error": "Failed to send email: [Errno 10054] Connection unexpectedly closed"
}
```

### Protocol Errors
```json
{
  "error": "Search failed: SEARCH failed: [CLIENTBUG] please select mailbox first"
}
```

## Malformed MIME Test Cases

See `tests/malformed_mime/` directory for test corpus.

### Test Categories
1. **Missing Boundaries**: Multipart messages with missing boundary markers
2. **Invalid Encoding**: Headers/body with invalid character encoding
3. **Corrupted Headers**: Missing required headers, malformed header values
4. **Nested Multipart**: Deeply nested multipart structures
5. **Missing Content-Type**: Messages without Content-Type headers
6. **Invalid Date Formats**: Various invalid date header formats
7. **Oversized Headers**: Headers exceeding normal limits
8. **Mixed Encoding**: Messages mixing different character encodings

## Recommendations

### Error Handling
- Always provide helpful error messages with actionable steps
- Mask credentials in logs (username@***)
- Implement retry logic with exponential backoff
- Handle network timeouts gracefully

### Connection Management
- Use single connection per agent namespace
- Implement connection pooling for multi-agent scenarios
- Auto-disconnect after operations when using auto-connect
- Handle connection drops gracefully

### Guardrails
- Enforce `MAX_BODY_BYTES` and `MAX_ATTACHMENT_BYTES`
- Truncate large content rather than failing
- Use sandbox mode for destructive operations during development

### Robustness
- Never crash on malformed input
- Return partial data when possible
- Log parsing errors for debugging
- Handle missing fields gracefully

---

**Last Updated**: December 3, 2025  
**Testing Platform**: GMX (primary), AOL (reference)  
**Status**: Complete

