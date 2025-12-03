# Troubleshooting Guide

## Common Issues and Solutions

### IMAP Connection Issues

#### Authentication Failed

**Symptoms:**
- Error: `authentication failed`
- Connection fails immediately

**Solutions:**
1. **Verify IMAP is enabled**: Go to GMX Settings > POP3 & IMAP and ensure IMAP access is enabled
2. **Wait for activation**: IMAP activation may take a few minutes to propagate after enabling
3. **Check 2FA status**: If using app-specific password, ensure 2FA is enabled
4. **Verify credentials**: Double-check username (full email) and password
5. **Check account lock**: Multiple failed attempts may temporarily lock the account

#### Connection Timeout

**Symptoms:**
- Connection hangs or times out
- No response from server

**Solutions:**
1. Check firewall settings (ports 993, 587, 465)
2. Verify SSL/TLS certificates are valid
3. Check network connectivity
4. Try different port (993 for IMAP, 587/465 for SMTP)

### SMTP Connection Issues

#### Connection Unexpectedly Closed

**Symptoms:**
- SMTP connection closes immediately
- Error: `Connection unexpectedly closed`

**Solutions:**
1. Try port 465 (SSL) instead of 587 (STARTTLS)
2. Verify SMTP server address (`mail.gmx.com` for GMX)
3. Check if account requires app-specific password
4. Ensure STARTTLS/TLS is enabled

#### Authentication Failed (SMTP)

**Symptoms:**
- SMTP login fails
- Same as IMAP authentication issues

**Solutions:**
- Same as IMAP authentication troubleshooting
- Use same app-specific password as IMAP

### Email Fetching Issues

#### Message Not Found

**Symptoms:**
- Error: `Message {uid} not found`
- Fetch fails for valid UID

**Solutions:**
1. Ensure mailbox is selected first
2. Verify UID is valid (use search to get current UIDs)
3. Check if message was deleted or moved
4. Re-select mailbox to refresh UID list

#### Malformed MIME

**Symptoms:**
- Email parsing fails
- Missing body or attachments

**Solutions:**
- Tool handles malformed MIME gracefully
- Check logs for specific parsing errors
- Body/attachments may be truncated if exceeding size limits

### UCW Wrapping Issues

#### UCW Cannot Parse CLI Tool

**Symptoms:**
- UCW parse/wrap fails
- Empty specification returned

**Solutions:**
1. Verify CLI tool has proper argparse structure
2. Check help text is clear and parseable
3. Ensure all commands have descriptions
4. Test CLI tool `--help` output manually

#### Wrapped Plugin Doesn't Work

**Symptoms:**
- Wrapped plugin fails to execute
- Commands not recognized

**Solutions:**
1. Verify wrapped plugin was generated correctly
2. Check file paths in wrapped plugin
3. Ensure original CLI tool is accessible
4. Test original CLI tool directly first

## GMX-Specific Issues

### IMAP Activation Delay

**Issue**: IMAP may take 5-15 minutes to activate after enabling in settings.

**Solution**: Wait a few minutes and retry connection.

### App-Specific Password Requirements

**Issue**: GMX requires 2FA to be enabled before app-specific passwords work.

**Solution**: Enable 2FA first, then generate app-specific password.

### Account Lockout

**Issue**: Multiple failed login attempts may temporarily lock account.

**Solution**: Wait 15-30 minutes before retrying, or log in via web to unlock.

## Performance Issues

### Slow Email Fetching

**Symptoms:**
- Fetching emails takes a long time
- Timeouts on large mailboxes

**Solutions:**
1. Use search to limit results before fetching
2. Fetch specific UIDs instead of all messages
3. Check network connection speed
4. Consider pagination for large mailboxes

### Large Attachments

**Symptoms:**
- Attachment fetch fails
- Memory issues

**Solutions:**
1. Attachments are truncated at `MAX_ATTACHMENT_BYTES` (25MB default)
2. Large attachments show `truncated: true` in response
3. Adjust `MAX_ATTACHMENT_BYTES` if needed

## Getting Help

If issues persist:
1. Check GMX account settings (IMAP enabled, 2FA status)
2. Verify credentials are correct
3. Test with a different email client to isolate issues
4. Check GMX support documentation
5. Review error messages for specific details

