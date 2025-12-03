# Setup Instructions

## Virtual Environment Setup

This project uses a Python virtual environment for dependency management and testing.

### Initial Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**:
   
   **Windows (PowerShell)**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   **Windows (CMD)**:
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   **Linux/macOS**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Development Workflow

Always activate the virtual environment before:
- Running tests
- Running the CLI tools
- Installing new dependencies
- Running UCW wrapping

### Testing

All tests should be run within the virtual environment:

```bash
# Activate venv first
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Run tests
pytest tests/
```

### Adding Dependencies

When adding new dependencies:

1. Activate virtual environment
2. Install package: `pip install package-name`
3. Update requirements.txt: `pip freeze > requirements.txt`

## Project Structure

```
smcp-imap-smtp/
├── venv/              # Virtual environment (git-ignored)
├── tools/             # CLI tools (IMAP/SMTP)
│   ├── imap/
│   └── smtp/
├── docs/              # Documentation
├── tests/             # Test suite
├── requirements.txt    # Python dependencies
└── SETUP.md           # This file
```

## Notes

- The virtual environment directory (`venv/`) is git-ignored
- Always use the virtual environment for development and testing
- Dependencies are managed via `requirements.txt`

