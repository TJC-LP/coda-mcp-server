# Coda MCP Server

A Model Context Protocol (MCP) server that provides seamless integration between Claude and Coda.io, enabling AI-powered document automation and data manipulation.

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
- **Export page content** - Get full HTML/Markdown content with `getPageContent`

### Table & Data Operations
- **List tables** - Find all tables and views in a doc
- **Get table details** - Access table metadata and structure
- **List columns** - Browse table columns with properties
- **Get column info** - Access column formulas and formats

### Row Operations
- **List rows** - Query and filter table data
- **Get specific rows** - Access individual row data
- **Insert/Update rows** - Add or modify data with `upsertRows`
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
2. **Python 3.11+**: Required for the MCP server

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

3. **Configure your API key**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and replace `changeme` with your Coda API key:
   ```
   CODA_API_KEY=your-actual-api-key-here
   ```

## Configuration for Claude Desktop

To use the Coda MCP server with Claude Desktop, you need to add it to your Claude Desktop configuration file.

### Configuration File Location

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Add the Coda MCP Server

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
      "args": ["run", "python", "/path/to/coda-mcp-server/src/coda_mcp_server/server.py"],
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
4. You should see 25 available Coda tools when you click `coda` in the dropdown and can toggle the ones that you need specifically.

## Usage in Claude

Once installed, you can use Coda operations directly in Claude by prefixing commands with `coda:`. Here are some examples:

### Document Operations
```
# List all your docs
Use coda:listDocs with isOwner: true, isPublished: false, query: ""

# Get info about a specific doc
Use coda:getDocInfo with docId: "your-doc-id"

# Create a new doc
Use coda:createDoc with title: "My New Doc"
```

### Working with Tables
```
# List tables in a doc
Use coda:listTables with docId: "your-doc-id"

# Get all rows from a table with column names
Use coda:listRows with docId: "your-doc-id", tableIdOrName: "Table Name", useColumnNames: true

# Insert a new row
Use coda:upsertRows with docId: "your-doc-id", tableIdOrName: "Table Name", rows: [{
  cells: [
    {column: "Name", value: "John Doe"},
    {column: "Email", value: "john@example.com"}
  ]
}]
```

### Page Content Export
```
# Get the full HTML content of a page
Use coda:getPageContent with docId: "your-doc-id", pageIdOrName: "Page Name"

# Get page content as Markdown
Use coda:getPageContent with docId: "your-doc-id", pageIdOrName: "Page Name", outputFormat: "markdown"
```

## API Reference

### Core Functions

#### Document Management
- `listDocs(isOwner, isPublished, query, ...)` - List available docs
- `getDocInfo(docId)` - Get document metadata
- `createDoc(title, sourceDoc?, timezone?, ...)` - Create new document
- `updateDoc(docId, title?, iconName?)` - Update document properties
- `deleteDoc(docId)` - Delete a document

#### Page Operations
- `listPages(docId, limit?, pageToken?)` - List pages in a doc
- `getPage(docId, pageIdOrName)` - Get page details
- `createPage(docId, name, subtitle?, ...)` - Create new page
- `updatePage(docId, pageIdOrName, ...)` - Update page properties
- `deletePage(docId, pageIdOrName)` - Delete a page
- `getPageContent(docId, pageIdOrName, outputFormat?)` - Export full page content

#### Table Operations
- `listTables(docId, limit?, sortBy?, ...)` - List all tables
- `getTable(docId, tableIdOrName)` - Get table details
- `listColumns(docId, tableIdOrName, ...)` - List table columns
- `getColumn(docId, tableIdOrName, columnIdOrName)` - Get column details

#### Row Operations
- `listRows(docId, tableIdOrName, query?, ...)` - List and filter rows
- `getRow(docId, tableIdOrName, rowIdOrName, ...)` - Get specific row
- `upsertRows(docId, tableIdOrName, rows, ...)` - Insert or update rows
- `updateRow(docId, tableIdOrName, rowIdOrName, row, ...)` - Update single row
- `deleteRow(docId, tableIdOrName, rowIdOrName)` - Delete single row
- `deleteRows(docId, tableIdOrName, rowIds)` - Delete multiple rows
- `pushButton(docId, tableIdOrName, rowIdOrName, columnIdOrName)` - Trigger button

#### Formula Operations
- `listFormulas(docId, limit?, sortBy?)` - List named formulas
- `getFormula(docId, formulaIdOrName)` - Get formula details

#### Authentication
- `whoami()` - Get current user information

## Development

### Project Structure
```
coda-mcp-server/
├── src/
│   ├── coda_mcp_server/
│   │   └── server.py      # Main MCP server implementation
│   └── resources/
│       └── coda-openapi.yml  # Coda API specification
├── .env.example           # Example environment configuration
├── pyproject.toml        # Project dependencies
└── README.md            # This file
```

### Running Locally for Development
```bash
# Install dependencies
uv sync

# Run the server directly
uv run python src/coda_mcp_server/server.py
```

## Troubleshooting

### Common Issues

1. **"API Error 401: Unauthorized"**
   - Check that your `CODA_API_KEY` in `.env` is correct
   - Ensure your API key has the necessary permissions

2. **"Rate limit exceeded"**
   - Coda API has rate limits; wait for the specified time before retrying
   - The server includes automatic rate limit detection

3. **Boolean parameters not working**
   - The server automatically converts boolean values to strings ("true"/"false")
   - This is handled internally, just use boolean values normally

4. **Page export issues**
   - Use `getPageContent` instead of manual export operations
   - This handles the entire export workflow automatically

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/TJC-LP/coda-mcp-server/issues) page.
