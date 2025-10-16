# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **MCP outputs now use snake_case** for Python consistency
  - All Pydantic models now serialize to snake_case by default (`serialize_by_alias=False`)
  - API requests still use camelCase (explicitly with `by_alias=True` in client.py)
  - Better Python/MCP ecosystem compatibility
  - Example: `browser_link` instead of `browserLink` in MCP responses

### Technical
- Updated all 83 Pydantic models with `serialize_by_alias=False` in ConfigDict
- Maintains camelCase for Coda API compatibility via explicit serialization
- Dual serialization: snake_case for MCP, camelCase for API

## [1.0.1] - 2025-10-16

### Added
- `.mcp.json` file for seamless Claude Code integration (uses dotenv for API key)

### Changed
- Updated README.md with Claude Code setup instructions
- Updated all README examples to use snake_case function names (v1.0.0 breaking change)
- Moved `load_dotenv()` before client initialization to ensure API key is loaded

### Fixed
- Claude Code integration now works out of the box (just set `.env`)
- API key initialization order (dotenv loaded before CodaClient creation)

### Removed
- `.mcp.example.json` (replaced with committed `.mcp.json` that uses dotenv)
- `.mcp.json` from .gitignore (safe to commit since API key is in .env)

## [1.0.0] - 2025-10-16

### 🎉 Major Release - Production Ready

This is a **major refactor** bringing the Coda MCP server to production quality with comprehensive type safety, modular architecture, and structured outputs. The refactor was motivated by fixing page export 404 errors and evolved into a complete architectural improvement.

### Added

**Type System (83 Pydantic Models):**
- Complete Pydantic models extracted from Coda OpenAPI specification
- 7 model modules: common, docs, pages, tables, rows, exports, formulas
- Full field descriptions and examples from OpenAPI spec
- ConfigDict for seamless camelCase/snake_case conversion
- Runtime request and response validation

**Structured Outputs:**
- Auto-generated output schemas for all 26 MCP tools
- FastMCP integration with Pydantic return types
- Better LLM understanding of response structure

**New Export Workflow:**
- `beginPageContentExport` - Initiate async page content export
- `getPageContentExportStatus` - Poll export status with auto-download
- Automatic content download when export completes (saves HTTP round-trip)
- Documented 404 retry strategy for server replication lag

**LLM Optimizations:**
- Explicit `description=` parameter on all 26 tools
- Action-oriented, concise descriptions (separate from developer docs)
- Flat argument signatures for ease of use
- Domain-organized tools (docs, pages, tables, rows, formulas)

### Changed

**Architecture (Complete Reorganization):**
- Split monolithic `server.py` (450 lines) into modular architecture (4,344 lines total)
- **client.py** (106 lines) - HTTP client with Pydantic auto-serialization
- **models/** (2,656 lines) - 83 Pydantic models across 7 modules
- **tools/** (1,082 lines) - Pure functions organized by domain (5 modules)
- **server.py** (700 lines) - Central MCP orchestrator with thin wrappers

**Code Quality Improvements:**
- 100% mypy type coverage (0 errors across 17 source files)
- Modern Pydantic v2 patterns (ConfigDict instead of class Config)
- Proper field aliases for API compatibility
- Comprehensive documentation throughout

**Dependencies:**
- Added pydantic for type validation
- Updated mypy configuration for pydantic plugin
- Added dev dependencies for quality checks

### BREAKING CHANGES

⚠️ **Function Names:** All tool functions renamed from camelCase to snake_case
```python
# Before (0.1.x)
getDocInfo, createDoc, listPages, updatePage, etc.

# After (1.0.0)
get_doc_info, create_doc, list_pages, update_page, etc.
```

⚠️ **CodaClient Attributes:** Internal attributes renamed to snake_case
```python
# Before
client.apiToken, client.baseUrl

# After
client.api_token, client.base_url
```

⚠️ **Export API Changed:**
- Removed: `getPageContent` (combined convenience method)
- Added: `beginPageContentExport` and `getPageContentExportStatus` (explicit workflow)
- Reason: Better error handling for server replication lag

⚠️ **Return Types:** All tools now return Pydantic models instead of `Any`
- This enables structured outputs but changes the return type
- FastMCP auto-serializes Pydantic models to JSON for MCP clients
- No breaking changes for MCP clients (JSON wire format unchanged)

⚠️ **Import Paths:** Internal reorganization may affect advanced usage
```python
# Before
from coda_mcp_server.server import CodaClient

# After
from coda_mcp_server.client import CodaClient
from coda_mcp_server.models import Doc, Page, Row  # New!
```

### Migration Guide

**For MCP Clients:**
- No changes required! MCP tool names updated automatically
- All tools accept same flat arguments
- Responses now have structured output schemas (improvement)

**For Python Library Users:**
- Update function names to snake_case if calling directly
- Update import paths if using CodaClient directly
- Tool functions now accept Pydantic models (see type hints)

**For Contributors:**
- Run `uv sync` to install new pydantic dependency
- Check `mypy src/` for type errors (should be 0)
- All tests should pass: `pytest tests/`

### Fixed
- Page export 404 errors due to server replication lag
- Missing type safety and validation
- Inconsistent naming conventions
- Monolithic code organization
- Missing structured output schemas

### Removed
- `getPageContent` convenience method (replaced with explicit workflow)
- TypedDict definitions (replaced with Pydantic models)
- Obsolete `test_async_utils.py` (functionality integrated)

### Documentation
- Added PHASE5_TYPE_VALIDATION_PLAN.md with implementation details
- Updated all docstrings with Args/Returns sections
- Added comprehensive model documentation from OpenAPI spec
- Improved error handling documentation

### Technical Details

**Quality Metrics:**
- mypy: 0 errors (17 source files)
- pytest: 16/16 tests passing
- ruff: All checks passed
- Type coverage: 0% → 100%
- Code size: 450 lines → 4,344 lines (well-organized)

**Performance:**
- Auto-download saves 1 HTTP request per page export
- Pydantic validation adds minimal overhead
- ConfigDict allows both snake_case and camelCase without conversion

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

[Unreleased]: https://github.com/TJC-LP/coda-mcp-server/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/TJC-LP/coda-mcp-server/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/TJC-LP/coda-mcp-server/compare/v0.1.1...v1.0.0
[0.1.1]: https://github.com/TJC-LP/coda-mcp-server/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/TJC-LP/coda-mcp-server/releases/tag/v0.1.0