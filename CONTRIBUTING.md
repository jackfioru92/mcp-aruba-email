# Contributing to MCP Aruba Email Server

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and considerate in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/mcp-aruba/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages or logs (sanitize any credentials!)

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its benefits
3. Provide use cases and examples
4. Discuss implementation approach if you have ideas

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/mcp-aruba.git
   cd mcp-aruba
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Set up development environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

4. **Make your changes**
   - Write clear, documented code
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

5. **Test your changes**
   ```bash
   # Run tests
   pytest tests/
   
   # Test manually
   python test_connection.py
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```
   
   Use clear commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `refactor:` for code refactoring
   - `test:` for tests

7. **Push and create PR**
   ```bash
   git push origin feature/amazing-feature
   ```
   Then open a Pull Request on GitHub

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and modular

```python
def send_email(
    to: str,
    subject: str,
    body: str,
    from_name: Optional[str] = None
) -> Dict:
    """Send an email via SMTP.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        from_name: Optional sender display name
        
    Returns:
        Dictionary with send status
        
    Raises:
        ConnectionError: If SMTP connection fails
        ValueError: If parameters are invalid
    """
    # Implementation
```

### Testing

- Write tests for new features
- Ensure existing tests pass
- Test with real Aruba account (use test account, not production)
- Test error handling paths

### Documentation

- Update README.md for user-facing changes
- Update EXAMPLES.md with usage examples
- Add inline comments for complex logic
- Update CHANGELOG.md

### Security

- **Never commit credentials** - Check .gitignore
- Sanitize logs and error messages
- Use environment variables for sensitive data
- Document security implications of changes

## Project Structure

```
mcp_aruba/
├── src/
│   └── mcp_aruba/
│       ├── __init__.py          # Package initialization
│       ├── server.py            # MCP server with tools
│       └── email_client.py      # IMAP/SMTP client
├── tests/                       # Test files
├── docs/                        # Additional documentation
├── .github/                     # GitHub-specific files
├── pyproject.toml              # Dependencies and metadata
├── README.md                   # Main documentation
├── EXAMPLES.md                 # Usage examples
├── CONTRIBUTING.md             # This file
└── LICENSE                     # MIT License
```

## Adding New Features

### Example: Adding a New MCP Tool

1. **Add to email_client.py**
   ```python
   def archive_email(self, email_id: str) -> Dict:
       """Archive an email."""
       # Implementation
   ```

2. **Add MCP tool in server.py**
   ```python
   @mcp.tool()
   def archive_email(email_id: str) -> dict[str, Any]:
       """Archive an email by ID."""
       try:
           with _get_email_client() as client:
               return client.archive_email(email_id)
       except Exception as e:
           return {"error": str(e)}
   ```

3. **Update documentation**
   - Add to README.md tool list
   - Add examples to EXAMPLES.md
   - Update CLAUDE_SETUP.md if needed

4. **Add tests**
   ```python
   def test_archive_email():
       # Test implementation
   ```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
4. Push tag: `git push origin v0.2.0`
5. Create GitHub release

## Getting Help

- 💬 [GitHub Discussions](https://github.com/yourusername/mcp-aruba/discussions) for questions
- 📧 [Issues](https://github.com/yourusername/mcp-aruba/issues) for bugs
- 📖 [Documentation](README.md) for usage help

## Recognition

Contributors will be recognized in:
- README.md contributors section
- GitHub contributors page
- Release notes

Thank you for contributing! 🎉
