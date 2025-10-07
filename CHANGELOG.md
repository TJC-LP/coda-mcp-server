# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Coda MCP Server
- Support for listing Coda documents
- Support for creating new Coda pages
- Support for reading Coda page content
- Support for updating existing Coda pages
- Support for listing tables in a document
- Support for listing rows in a table
- Support for creating new rows in a table
- Support for updating existing rows
- Comprehensive error handling and validation
- Type hints throughout the codebase
- Pre-commit hooks for code quality
- GitHub Actions workflows for CI/CD
- Security scanning with Safety and Bandit
- Automated PyPI publishing on releases

### Security
- API tokens are handled securely via environment variables
- No sensitive information is logged

## [0.1.0] - TBD

Initial release.

[Unreleased]: https://github.com/TJC-LP/coda-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/TJC-LP/coda-mcp-server/releases/tag/v0.1.0