# Concurrency Model

This document describes the concurrency model for IMAP/SMTP tools and how to safely use them in multi-agent environments.

## Current Architecture

### Connection Model

**One Connection Per CLI Invocation:**
- Each CLI command creates its own connection, performs the operation, and disconnects
- Commands are **self-contained** - no shared state between invocations
- This ensures **thread-safety by isolation**

### Auto-Connect Pattern

All commands support auto-connect:
- If no active connection exists, commands automatically connect using provided credentials
- After the operation completes, the connection is automatically closed
- This pattern ensures each command is independent and safe for concurrent execution

## Multi-Agent Scenarios

### Recommended Pattern: One Connection Per Agent Namespace

**For SMCP/LettaAI agents:**
- Each agent should use its own connection
- Connections are created per-command and closed after use
- No shared connection state between agents

**Example:**
```python
# Agent 1
python tools/imap/cli.py search --criteria "ALL" --account agent1

# Agent 2 (concurrent, independent)
python tools/imap/cli.py search --criteria "UNSEEN" --account agent2
```

### Connection Pooling (Future Enhancement)

For high-concurrency scenarios, connection pooling could be implemented:
- Pool of IMAP connections per account
- Request queue for concurrent access
- Connection reuse for better performance

**Current Status:** Not implemented - each command uses its own connection.

## Thread Safety

### IMAP Client (`imapclient`)

**Thread Safety:**
- `imapclient` is **not thread-safe** for shared connections
- Multiple threads accessing the same `IMAPClient` instance can cause issues

**Our Solution:**
- Each command creates its own `IMAPConnection` instance
- Connections are not shared between commands
- This ensures thread-safety through isolation

### SMTP Client (`smtplib`)

**Thread Safety:**
- `smtplib.SMTP` is **not thread-safe** for shared connections
- Similar to IMAP, we use connection isolation

**Our Solution:**
- Each command creates its own `SMTPConnection` instance
- No shared state between commands

## Rate Limiting

### Current Implementation

**No Built-in Rate Limiting:**
- Commands execute immediately when called
- No throttling or queuing

### Recommended Patterns

**For Production Use:**

1. **Application-Level Rate Limiting:**
   - Implement rate limiting in the calling application (SMCP server, agent framework)
   - Limit requests per account per time period
   - Example: Max 10 requests per minute per account

2. **Connection-Level Limits:**
   - Some email providers have connection limits
   - GMX: Typically allows 1-2 concurrent connections per account
   - Our auto-connect/disconnect pattern naturally respects these limits

3. **Exponential Backoff:**
   - Implement retry logic with exponential backoff for transient failures
   - Handle rate limit errors gracefully

### Example Rate Limiting (Application Level)

```python
from collections import defaultdict
from time import time
from threading import Lock

class RateLimiter:
    def __init__(self, max_requests=10, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def allow(self, account_name):
        with self.lock:
            now = time()
            # Clean old requests
            self.requests[account_name] = [
                req_time for req_time in self.requests[account_name]
                if now - req_time < self.window_seconds
            ]
            
            # Check limit
            if len(self.requests[account_name]) >= self.max_requests:
                return False
            
            # Record request
            self.requests[account_name].append(now)
            return True

# Usage in SMCP server
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

def handle_imap_request(account_name, command):
    if not rate_limiter.allow(account_name):
        return {"error": "Rate limit exceeded"}
    # Execute command...
```

## Best Practices

### For Agent Developers

1. **Use Account Profiles:**
   - Store credentials in profiles, not in code
   - Use `--account` flag for all commands

2. **Handle Errors Gracefully:**
   - Network errors are transient
   - Implement retry logic with backoff
   - Don't retry authentication failures

3. **Respect Rate Limits:**
   - Don't spam email servers
   - Implement delays between bulk operations
   - Use sandbox mode during development

4. **Connection Management:**
   - Let auto-connect handle connections
   - Don't try to maintain persistent connections
   - Each command is self-contained

### For SMCP Server Maintainers

1. **Implement Rate Limiting:**
   - Add rate limiting at the SMCP server level
   - Per-account limits
   - Per-agent limits

2. **Connection Pooling (Optional):**
   - For high-concurrency scenarios
   - Pool connections per account
   - Queue requests when pool is exhausted

3. **Error Handling:**
   - Catch and log connection errors
   - Retry transient failures
   - Don't retry authentication failures

## Performance Considerations

### Current Performance

- **Connection Overhead:** ~100-200ms per command (connect + operation + disconnect)
- **Acceptable for:** Most agent use cases (not high-frequency trading)
- **Bottleneck:** Network I/O, not Python

### Optimization Opportunities

1. **Connection Reuse:**
   - Keep connections alive for multiple commands
   - Reduces connection overhead
   - Requires connection pooling implementation

2. **Batch Operations:**
   - Fetch multiple emails in one command
   - Reduce round-trips
   - Already supported via `--message-ids` (multiple IDs)

3. **Async Operations:**
   - Use `asyncio` for concurrent operations
   - Not currently implemented
   - Would require async IMAP/SMTP libraries

## Testing Concurrency

See `tests/test_concurrency.py` for concurrency tests:
- Multiple independent connections
- Concurrent fetch operations
- Connection isolation

## Future Enhancements

1. **Connection Pooling:**
   - Pool of connections per account
   - Automatic connection reuse
   - Better performance for high-concurrency

2. **Async Support:**
   - Async IMAP/SMTP operations
   - Better for high-concurrency scenarios
   - Requires async libraries

3. **Built-in Rate Limiting:**
   - Configurable rate limits
   - Per-account limits
   - Automatic backoff

---

**Last Updated:** December 3, 2025  
**Status:** Current implementation documented

