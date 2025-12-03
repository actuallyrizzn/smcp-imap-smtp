# UCW-Compatible CLI Tool Requirements

## Overview

This document outlines the requirements for building CLI tools that UCW (Universal Command Wrapper) can automatically wrap into SMCP plugins. Based on analysis of UCW and existing SMCP plugin examples.

## UCW Analysis

### What UCW Does

UCW (Universal Command Wrapper) can:
1. **Parse command help text** - Extracts commands, options, and arguments from `--help` output
2. **Generate SMCP plugins** - Creates complete SMCP plugin files from CLI tools
3. **Execute commands** - Wraps commands with proper argument handling
4. **Output JSON** - In SMCP mode, all output is JSON

### UCW Expectations

From analyzing `ucw/cli.py` and documentation:

1. **Standard argparse structure** - UCW parses standard argparse help text
2. **JSON output** - Commands should output JSON (not plain text) for SMCP compatibility
3. **Error handling** - Errors should be JSON objects: `{"error": "message"}` or `{"status": "error", "error": "message"}`
4. **Subcommands** - Use argparse subparsers for multiple commands
5. **Help text** - Clear help text that UCW can parse

## SMCP Plugin Examples Analysis

### BotFather Plugin Structure

**Location**: `tmp/smcp-analysis/plugins/botfather/cli.py`

**Key Patterns**:
- Uses `argparse` with subparsers for commands
- Each command function takes a dict of arguments
- Returns dict with results or errors
- Outputs JSON via `json.dumps(result, indent=2)`
- Exit codes: 0 for success, 1 for error
- Error format: `{"error": "message"}`

**Example**:
```python
def click_button(args: Dict[str, Any]) -> Dict[str, Any]:
    """Click a button in a BotFather message."""
    button_text = args.get("button-text")
    msg_id = args.get("msg-id")
    
    if not button_text or not msg_id:
        return {"error": "Missing required arguments: button-text and msg-id"}
    
    # Implementation...
    return {"result": f"Clicked button {button_text} on message {msg_id}"}
```

### DevOps Plugin Structure

**Location**: `tmp/smcp-analysis/plugins/devops/cli.py`

**Key Patterns**:
- Same structure as BotFather
- Commands return dicts with `result` or `error` keys
- JSON output for all responses
- Clear error messages

## UCW-Compatible CLI Tool Requirements

### 1. Command Structure

**Required**: Use `argparse` with subparsers

```python
import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Plugin description")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command parsers
    cmd_parser = subparsers.add_parser("command-name", help="Command description")
    cmd_parser.add_argument("--param", required=True, help="Parameter description")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command and output JSON
    result = execute_command(args)
    print(json.dumps(result, indent=2))
    sys.exit(0 if "error" not in result else 1)
```

### 2. JSON Output Format

**Required**: All commands must output JSON

**Success format**:
```json
{
  "status": "success",
  "result": "command result data"
}
```

**Error format**:
```json
{
  "status": "error",
  "error": "Error message"
}
```

**Alternative (simpler)**:
```json
{
  "result": "success data"
}
```
or
```json
{
  "error": "error message"
}
```

### 3. Error Handling

**Required**: Errors must be JSON objects, not plain text

```python
try:
    result = execute_command(args)
    print(json.dumps(result, indent=2))
    sys.exit(0 if "error" not in result else 1)
except Exception as e:
    error_result = {"error": str(e)}
    print(json.dumps(error_result, indent=2))
    sys.exit(1)
```

### 4. Logging

**Important**: Log to stderr, not stdout (stdout is for JSON)

```python
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr, not stdout
)
```

### 5. Help Text

**Required**: Clear help text that UCW can parse

UCW looks for:
- Command descriptions in `help` parameters
- Parameter descriptions in `add_argument(help=...)`
- Epilog with "Available commands:" section (optional, for fallback)

**Example**:
```python
parser = argparse.ArgumentParser(
    description="IMAP email reading plugin",
    epilog="""
Available commands:
  connect          Connect to IMAP server
  list-mailboxes   List all mailboxes
  fetch            Fetch email content
    """
)
```

### 6. Command Execution Pattern

**Recommended pattern**:

```python
def execute_command(args):
    """Execute command with args."""
    # Validate arguments
    if not args.required_param:
        return {"error": "Missing required parameter: required_param"}
    
    try:
        # Execute command logic
        result = do_work(args.required_param, args.optional_param)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
```

## IMAP/SMTP CLI Tool Structure

### Directory Structure

```
tools/
├── imap/
│   ├── cli.py          # Main CLI interface
│   ├── README.md       # Documentation
│   └── __init__.py     # Optional package init
└── smtp/
    ├── cli.py          # Main CLI interface
    ├── README.md       # Documentation
    └── __init__.py     # Optional package init
```

### IMAP CLI Commands

Based on project plan, IMAP CLI should support:

1. `connect` - Connect to IMAP server
2. `list-mailboxes` - List all mailboxes
3. `select-mailbox` - Select a mailbox
4. `search` - Search emails
5. `fetch` - Fetch email content
6. `mark-read` - Mark as read
7. `mark-unread` - Mark as unread
8. `delete` - Delete emails (sandbox-aware)
9. `move` - Move emails (sandbox-aware)
10. `disconnect` - Disconnect from server

### SMTP CLI Commands

Based on project plan, SMTP CLI should support:

1. `connect` - Connect to SMTP server
2. `send` - Send plain text email
3. `send-html` - Send HTML email
4. `send-with-attachment` - Send email with attachments
5. `disconnect` - Disconnect from server

## UCW Wrapping Process

### How UCW Wraps CLI Tools

1. **Parse help text**: UCW runs `python cli.py --help` and parses output
2. **Extract commands**: Finds subcommands from argparse help
3. **Extract parameters**: Parses argument definitions
4. **Generate wrapper**: Creates SMCP plugin file with tool definitions
5. **Execute commands**: Wraps command execution with proper argument passing

### Testing with UCW

```bash
# Test UCW can parse the CLI tool
python ucw/cli.py parse tools/imap/cli.py

# Generate SMCP plugin from CLI tool
python ucw/cli.py wrap tools/imap/cli.py --output plugins/imap/cli.py

# Test wrapped plugin
python plugins/imap/cli.py connect --server imap.aol.com --username test@aol.com --password pass
```

## Key Takeaways

1. **Build standard CLI tools** - Not SMCP plugins directly
2. **Use argparse** - Standard library, UCW can parse it
3. **Output JSON** - All commands must output JSON
4. **Error handling** - Errors as JSON objects
5. **Log to stderr** - Keep stdout clean for JSON
6. **Clear help text** - UCW needs to parse it
7. **Test with UCW early** - Validate UCW can wrap your tools

## Next Steps

1. Build IMAP CLI tool following these requirements
2. Build SMTP CLI tool following these requirements
3. Test both with UCW to verify wrapping works
4. Use UCW to generate SMCP plugins
5. Deploy wrapped plugins to SMCP server

---

**Document Status**: Initial analysis complete  
**Last Updated**: December 2, 2025

