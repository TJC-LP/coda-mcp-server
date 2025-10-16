# Coda MCP Server

[![PyPI version](https://img.shields.io/pypi/v/coda-mcp-server.svg)](https://pypi.org/project/coda-mcp-server/)
[![Python versions](https://img.shields.io/pypi/pyversions/coda-mcp-server.svg)](https://pypi.org/project/coda-mcp-server/)
[![License](https://img.shields.io/github/license/TJC-LP/coda-mcp-server.svg)](https://github.com/TJC-LP/coda-mcp-server/blob/main/LICENSE)
[![Tests](https://github.com/TJC-LP/coda-mcp-server/workflows/CI/badge.svg)](https://github.com/TJC-LP/coda-mcp-server/actions)

A Model Context Protocol (MCP) server that provides seamless integration between Claude and Coda.io, enabling AI-powered document automation and data manipulation.

> **Note**: This is an unofficial MCP server developed by TJC L.P. and is not affiliated with, endorsed by, or supported by Coda. For official Coda support and documentation, please visit [coda.io](https://coda.io).

> **Note**: Version 1.1.0+ uses `snake_case` field names (e.g., `browser_link` instead of `browserLink`) for Python ecosystem compatibility. See [CHANGELOG](CHANGELOG.md#110---2025-10-16) for migration details if upgrading from 1.0.x.

## Features

### Document Operations
- **List documents** - Search and filter your Coda docs
- **Create documents** - Generate new docs with optional templates
- **Read document info** - Get metadata about any doc
- **Update documents** - Modify doc properties like title and icon
- **Delete documents** - Remove docs (use with caution!)

### Page Management
- **List pages** - Browse all pages in a doc
- **Create pages** - Add new pages with rich content
- **Read pages** - Get page details and content
- **Update pages** - Modify page properties and content
- **Delete pages** - Remove pages from docs
- **Export page content** - Get full HTML/Markdown content with `begin_page_content_export` and `get_page_content_export_status`

### Table & Data Operations
- **List tables** - Find all tables and views in a doc
- **Get table details** - Access table metadata and structure
- **List columns** - Browse table columns with properties
- **Get column info** - Access column formulas and formats

### Row Operations
- **List rows** - Query and filter table data
- **Get specific rows** - Access individual row data
- **Insert/Update rows** - Add or modify data with `upsert_rows`
- **Update single row** - Modify specific row data
- **Delete rows** - Remove single or multiple rows
- **Push buttons** - Trigger button columns in tables

### Formula Operations
- **List formulas** - Find all named formulas in a doc
- **Get formula details** - Access formula expressions

### Authentication
- **Who am I** - Get current user information

## Installation

### Prerequisites

1. **Coda API Key**: Get your API token from [Coda Account Settings](https://coda.io/account)
2. **Python 3.11+ (including 3.14)**: Required for the MCP server

### Option 1: Install from PyPI (Recommended)

The Coda MCP server is available on PyPI and can be installed directly using `uvx` (recommended) or `pip`:

```bash
# Using uvx (no installation needed, just run)
uvx coda-mcp-server

# Or install globally with pip
pip install coda-mcp-server
```

### Option 2: Install from Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/TJC-LP/coda-mcp-server.git
   cd coda-mcp-server
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set your API key as an environment variable** (see Configuration section below)

## Configuration

### Option 1: Claude Code (Recommended for Development)

For using with Claude Code during development:

1. **Set your API key as a shell environment variable:**
   ```bash
   # Add to your shell profile (~/.zshrc, ~/.bashrc, etc.)
   export CODA_API_KEY="your-coda-api-key-here"

   # Or set it for the current session
   export CODA_API_KEY="your-coda-api-key-here"
   ```

2. **MCP configuration is already included!**

   The repository includes a `.mcp.json` file that automatically configures the Coda MCP server:
   ```json
   {
     "mcpServers": {
       "coda": {
         "command": "uv",
         "args": ["run", "coda-mcp-server"],
         "env": {
           "CODA_API_KEY": "${CODA_API_KEY}"
         }
       }
     }
   }
   ```

   The `${CODA_API_KEY}` syntax reads the API key from your shell environment.

3. **Reload Claude Code** - The MCP server will be automatically available

> **Security Note:** API keys are read from your shell environment, not from files. This prevents accidental commits and arbitrary file loading.

**Alternative: Using `.env` files with dotenv-cli**

If you prefer file-based configuration, you can use `dotenv-cli` to inject environment variables:

```bash
# Create .env file from example (gitignored)
cp .env.example .env
# Edit .env and replace 'changeme' with your API key

# Run Claude Code with dotenv (no installation needed)
bunx dotenv-cli -- claude
# or
npx dotenv-cli -- claude
```

### Option 2: Claude Desktop

To use the Coda MCP server with Claude Desktop, you need to add it to your Claude Desktop configuration file.

**Configuration File Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Add the Coda MCP Server:**

Edit the configuration file and add the Coda server to the `mcpServers` section:

```json
{
  "mcpServers": {
    "coda": {
      "command": "uvx",
      "args": ["coda-mcp-server"],
      "env": {
        "CODA_API_KEY": "your-coda-api-key-here"
      }
    }
  }
}
```

> **Important**: Replace `your-coda-api-key-here` with your actual Coda API key from [Coda Account Settings](https://coda.io/account).

### Alternative: Using Local Installation

If you installed from source, you can point to your local installation:

```json
{
  "mcpServers": {
    "coda": {
      "command": "uv",
      "args": [
         "run", 
         "--directory", 
         "/path/to/repo",
         "coda-mcp-server"
      ],
      "env": {
        "CODA_API_KEY": "your-coda-api-key-here"
      }
    }
  }
}
```

### Verify Installation

After adding the configuration:
1. Restart Claude Desktop
2. Look for the settings icon in the bottom of your conversation
3. Click it and verify that "coda" is listed as a connected server
4. You should see 26 available Coda tools when you click `coda` in the dropdown and can toggle the ones that you need specifically.

## Usage in Claude

Once installed, you can use Coda operations directly in Claude by prefixing commands with `coda:`. Here are some examples:

### Document Operations
```
# List all your docs
Use coda:list_docs with is_owner: true, is_published: false, query: ""

# Get info about a specific doc
Use coda:get_doc_info with doc_id: "your-doc-id"

# Create a new doc
Use coda:create_doc with title: "My New Doc"
```

### Working with Tables
```
# List tables in a doc
Use coda:list_tables with doc_id: "your-doc-id"

# Get all rows from a table with column names
Use coda:list_rows with doc_id: "your-doc-id", table_id_or_name: "Table Name", use_column_names: true

# Insert a new row
Use coda:upsert_rows with doc_id: "your-doc-id", table_id_or_name: "Table Name", rows_data: [{
  cells: [
    {column: "Name", value: "John Doe"},
    {column: "Email", value: "john@example.com"}
  ]
}]
```

### Page Content Export
```
# Start page export
Use coda:begin_page_content_export with doc_id: "your-doc-id", page_id_or_name: "Page Name", output_format: "markdown"

# Check export status and get content
Use coda:get_page_content_export_status with doc_id: "your-doc-id", page_id_or_name: "Page Name", request_id: "request-id-from-previous-step"
```

## API Reference

### Core Functions

#### Document Management
- `list_docs(is_owner, is_published, query, ...)` - List available docs
- `get_doc_info(doc_id)` - Get document metadata
- `create_doc(title, source_doc?, timezone?, ...)` - Create new document
- `update_doc(doc_id, title?, icon_name?)` - Update document properties
- `delete_doc(doc_id)` - Delete a document

#### Page Operations
- `list_pages(doc_id, limit?, page_token?)` - List pages in a doc
- `get_page(doc_id, page_id_or_name)` - Get page details
- `create_page(doc_id, name, subtitle?, ...)` - Create new page
- `update_page(doc_id, page_id_or_name, ...)` - Update page properties
- `delete_page(doc_id, page_id_or_name)` - Delete a page
- `begin_page_content_export(doc_id, page_id_or_name, output_format?)` - Start async page export
- `get_page_content_export_status(doc_id, page_id_or_name, request_id)` - Poll export status and download content

#### Table Operations
- `list_tables(doc_id, limit?, sort_by?, ...)` - List all tables
- `get_table(doc_id, table_id_or_name)` - Get table details
- `list_columns(doc_id, table_id_or_name, ...)` - List table columns
- `get_column(doc_id, table_id_or_name, column_id_or_name)` - Get column details

#### Row Operations
- `list_rows(doc_id, table_id_or_name, query?, ...)` - List and filter rows
- `get_row(doc_id, table_id_or_name, row_id_or_name, ...)` - Get specific row
- `upsert_rows(doc_id, table_id_or_name, rows_data, ...)` - Insert or update rows
- `update_row(doc_id, table_id_or_name, row_id_or_name, row, ...)` - Update single row
- `delete_row(doc_id, table_id_or_name, row_id_or_name)` - Delete single row
- `delete_rows(doc_id, table_id_or_name, row_ids)` - Delete multiple rows
- `push_button(doc_id, table_id_or_name, row_id_or_name, column_id_or_name)` - Trigger button

#### Formula Operations
- `list_formulas(doc_id, limit?, sort_by?)` - List named formulas
- `get_formula(doc_id, formula_id_or_name)` - Get formula details

#### Authentication
- `whoami()` - Get current user information

## Development

### Project Structure
```
coda-mcp-server/
├── src/
│   ├── coda_mcp_server/
│   │   ├── server.py        # MCP server orchestrator (700 lines)
│   │   ├── client.py        # HTTP client with Pydantic serialization
│   │   ├── models/          # 83 Pydantic models (7 modules)
│   │   │   ├── __init__.py
│   │   │   ├── common.py    # Shared types and base models
│   │   │   ├── docs.py      # Document models
│   │   │   ├── pages.py     # Page models
│   │   │   ├── tables.py    # Table and column models
│   │   │   ├── rows.py      # Row and cell models
│   │   │   ├── exports.py   # Export workflow models
│   │   │   └── formulas.py  # Formula models
│   │   └── tools/           # Pure functions (5 modules)
│   │       ├── __init__.py
│   │       ├── docs.py      # Document operations
│   │       ├── pages.py     # Page operations
│   │       ├── tables.py    # Table operations
│   │       ├── rows.py      # Row operations
│   │       └── formulas.py  # Formula operations
│   └── resources/
│       └── coda-openapi.yml  # Coda API specification
├── tests/                    # 44 tests
│   ├── conftest.py
│   ├── test_models.py
│   └── test_client_requests.py
├── .env.example
├── .mcp.json                 # Claude Code integration
└── pyproject.toml
```

### Running Locally for Development
```bash
# Install dependencies
uv sync

# Set your API key (if not already in your shell profile)
export CODA_API_KEY="your-coda-api-key-here"

# Run the server directly
uv run python src/coda_mcp_server/server.py
```

## Troubleshooting

### Common Issues

1. **"API Error 401: Unauthorized"**
   - Check that your `CODA_API_KEY` environment variable is set correctly
   - Verify with: `echo $CODA_API_KEY`
   - Ensure your API key has the necessary permissions

2. **"Rate limit exceeded"**
   - Coda API has rate limits; wait for the specified time before retrying
   - The server includes automatic rate limit detection

3. **Boolean parameters not working**
   - The server automatically converts boolean values to strings ("true"/"false")
   - This is handled internally, just use boolean values normally

4. **Page export issues**
   - Use the two-step export workflow: `begin_page_content_export` then `get_page_content_export_status`
   - The status check automatically downloads content when ready

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/TJC-LP/coda-mcp-server/issues) page.
