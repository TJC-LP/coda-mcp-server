# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within Coda MCP Server, please send an email to security@yourdomain.com. All security vulnerabilities will be promptly addressed.

Please do not report security vulnerabilities through public GitHub issues.

### What to include in your report

Please include the following details in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Possible impact of the vulnerability
- Any suggested fixes or workarounds

### What to expect

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will provide a more detailed response within 7 days indicating the next steps in handling your report
- We will keep you informed about the progress towards a fix and full announcement
- We may ask for additional information or guidance

## Security Update Process

1. The security report is received and assigned to a primary handler
2. The problem is confirmed and a list of all affected versions is determined
3. Code audit is performed to find any potential similar problems
4. Fixes are prepared for all supported releases
5. A security advisory is created and published

## Security Best Practices for Users

### API Token Security

- **Never commit your Coda API token to version control**
- Store your API token in environment variables or secure credential storage
- Use `.env` files for local development (already included in `.gitignore`)
- Rotate your API tokens regularly
- Use tokens with minimal required permissions

### Environment Setup

1. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

2. Add your Coda API token:
   ```
   CODA_API_TOKEN=your-actual-token-here
   ```

3. Ensure `.env` is in your `.gitignore` (it already is by default)

### Dependencies

- We use automated security scanning with Safety and Bandit
- Dependencies are regularly updated via Dependabot
- All pull requests undergo security review
- We follow the principle of least privilege for all operations

### Data Handling

- This tool interacts with your Coda documents and data
- Always verify the operations before execution
- Use read-only tokens when possible for querying operations
- Be cautious when granting write permissions

## Security Features

### Built-in Security Measures

1. **Input Validation**: All inputs are validated before processing
2. **Error Handling**: Sensitive information is never exposed in error messages
3. **Secure Communication**: All API calls use HTTPS
4. **Token Handling**: API tokens are never logged or exposed
5. **Dependency Scanning**: Automated vulnerability scanning in CI/CD

### Recommended Security Configuration

For production use, we recommend:

1. Using environment-specific API tokens
2. Implementing rate limiting on your Coda API usage
3. Monitoring API usage for unusual patterns
4. Regular security audits of your implementation

## Acknowledgments

We would like to thank the following individuals for responsibly disclosing security issues:

- [List will be updated as vulnerabilities are reported and fixed]

## Contact

For any security-related questions or concerns, please contact:
- Email: security@yourdomain.com
- PGP Key: [Link to PGP key if available]