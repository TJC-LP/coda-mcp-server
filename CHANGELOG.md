# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2025-01-07

### Changed
- Updated all repository URLs from placeholder to TJC-LP organization
- Added disclaimer clarifying unofficial MCP server status and TJC L.P. development

### Documentation
- Updated pyproject.toml with correct GitHub URLs
- Updated CONTRIBUTING.md with correct repository links
- Updated README.md with disclaimer note
- Updated CHANGELOG.md with correct version links

## [0.1.0] - 2025-01-06

Initial release.

### Added
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

[Unreleased]: https://github.com/TJC-LP/coda-mcp-server/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/TJC-LP/coda-mcp-server/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/TJC-LP/coda-mcp-server/releases/tag/v0.1.0