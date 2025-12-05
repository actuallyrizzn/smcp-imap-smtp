# Sent Folder Research: Why Sent Messages Don't Appear

## Problem

When sending emails via SMTP, sent messages don't automatically appear in the "Sent" or "Sent Items" folder when checked via IMAP.

## Root Cause

**SMTP protocol doesn't save sent messages** - SMTP is designed only for transmitting emails, not storing them. The protocol has no concept of "saving a copy to Sent folder."

## Provider Behavior

Different email providers handle this differently:

1. **Gmail**: Automatically saves sent messages to Sent folder (server-side)
2. **GMX**: Does NOT automatically save sent messages when using SMTP directly
3. **AOL**: Similar behavior - may or may not save depending on configuration
4. **Most providers**: Don't automatically save when using SMTP directly

## Solution: IMAP APPEND

The standard solution used by email clients is:

1. **Send email via SMTP** (what we currently do)
2. **Save the message** (we have it in memory as `msg.as_string()`)
3. **Connect to IMAP** (we have IMAP client available)
4. **APPEND message to Sent folder** (using IMAP APPEND command)

## Implementation Plan

### Option 1: Automatic Save (Recommended)
- After successful SMTP send, automatically APPEND to Sent folder
- Requires IMAP credentials (can use same account profile)
- Add `--save-to-sent` flag (default: True) to allow disabling

### Option 2: Manual Save
- Add separate `save-to-sent` command
- User must explicitly call it after sending
- More control but less convenient

### Option 3: Optional Flag
- Add `--save-to-sent` flag (default: False)
- User opts in when they want it
- Most flexible but requires user awareness

## Technical Details

### IMAP APPEND Command
```python
# Using imapclient
imap_client.append('Sent', message_bytes, flags=['\\Seen'])
```

### Message Format
- Use the same `msg.as_string()` or `msg.as_bytes()` from SMTP send
- Must be in RFC822 format (which email.message already provides)

### Folder Names
Different providers use different names:
- GMX: "Sent" or "Gesendet"
- Gmail: "[Gmail]/Sent Mail"
- AOL: "Sent"
- Outlook: "Sent Items"

Should detect/allow configuration of Sent folder name.

## Recommendation

**Implement Option 1 with opt-out flag:**
- Default behavior: Save to Sent folder automatically
- Add `--no-save-to-sent` flag to disable
- Use account profile for IMAP connection (same credentials)
- Handle gracefully if IMAP connection fails (don't fail the send)
- Log warning if Sent folder doesn't exist or append fails

This matches how most email clients work (Outlook, Thunderbird, Apple Mail all do this automatically).

