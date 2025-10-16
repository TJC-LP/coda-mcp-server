"""Coda MCP server - main entry point and tool registration."""

from typing import Any, Literal

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .client import CodaClient
from .models import (
    BeginPageContentExportRequest,
    BeginPageContentExportResponse,
    Column,
    ColumnList,
    Doc,
    DocCreate,
    DocDelete,
    DocList,
    DocumentCreationResult,
    DocUpdate,
    DocUpdateResult,
    InitialPage,
    Page,
    PageContent,
    PageContentExportStatusResponse,
    PageContentUpdate,
    PageCreate,
    PageCreateResult,
    PageDeleteResult,
    PageList,
    PageUpdate,
    PageUpdateResult,
    PushButtonResult,
    Row,
    RowDeleteResult,
    RowEdit,
    RowList,
    RowsDeleteResult,
    RowsUpsertResult,
    RowUpdateResult,
    Table,
    TableList,
)
from .tools import docs, formulas, pages, rows, tables

# Central MCP server instance
mcp = FastMCP("coda", dependencies=["aiohttp"])
client = CodaClient()

# ============================================================================
# Doc Tools
# ============================================================================


@mcp.tool(
    description="Get information about the current authenticated Coda user including name, email, and scoped token info"
)
async def whoami() -> Any:
    """Get information about the current authenticated user.

    Returns:
        User information including name, email, and scoped token info.
    """
    return await docs.whoami(client)


@mcp.tool(
    description="Get detailed metadata about a specific Coda doc by its ID"
)
async def get_doc_info(doc_id: str) -> Doc:
    """Get info about a particular doc."""
    return await docs.get_doc_info(client, doc_id)


@mcp.tool(
    description="Permanently delete a Coda doc by ID - use with extreme caution as this cannot be undone"
)
async def delete_doc(doc_id: str) -> DocDelete:
    """Delete a doc. USE WITH CAUTION."""
    return await docs.delete_doc(client, doc_id)


@mcp.tool(
    description="Update properties of a Coda doc including title and icon"
)
async def update_doc(doc_id: str, title: str | None = None, icon_name: str | None = None) -> DocUpdateResult:
    """Update properties of a doc."""
    request = DocUpdate(title=title, icon_name=icon_name)
    return await docs.update_doc(client, doc_id, request)


@mcp.tool(
    description=(
        "List Coda docs accessible by the user with filtering options - "
        "returns docs in reverse chronological order by most recent activity"
    )
)
async def list_docs(
    is_owner: bool,
    is_published: bool,
    query: str,
    source_doc: str | None = None,
    is_starred: bool | None = None,
    in_gallery: bool | None = None,
    workspace_id: str | None = None,
    folder_id: str | None = None,
    limit: int | None = None,
    page_token: str | None = None,
) -> DocList:
    """List available docs.

    Returns a list of Coda docs accessible by the user, and which they have opened at least once.
    These are returned in the same order as on the docs page: reverse chronological by the latest
    event relevant to the user (last viewed, edited, or shared).

    Args:
        is_owner: Show only docs owned by the user.
        is_published: Show only published docs.
        query: Search term used to filter down results.
        source_doc: Show only docs copied from the specified doc ID.
        is_starred: If true, returns docs that are starred. If false, returns docs that are not starred.
        in_gallery: Show only docs visible within the gallery.
        workspace_id: Show only docs belonging to the given workspace.
        folder_id: Show only docs belonging to the given folder.
        limit: Maximum number of results to return in this query (default: 25).
        page_token: An opaque token used to fetch the next page of results.

    Returns:
        Dictionary containing document list and pagination info.
    """
    return await docs.list_docs(
        client,
        is_owner,
        is_published,
        query,
        source_doc,
        is_starred,
        in_gallery,
        workspace_id,
        folder_id,
        limit,
        page_token,
    )


@mcp.tool(
    description=(
        "Create a new Coda doc with optional configuration including title, timezone, "
        "folder/workspace placement, and initial page content"
    )
)
async def create_doc(
    title: str,
    source_doc: str | None = None,
    timezone: str | None = None,
    folder_id: str | None = None,
    workspace_id: str | None = None,
    initial_page: InitialPage | None = None,
) -> DocumentCreationResult:
    """Create a new Coda doc.

    Args:
        title: Title of the new doc.
        source_doc: Optional ID of a doc to copy.
        timezone: Timezone for the doc, e.g. 'America/Los_Angeles'.
        folder_id: ID of the folder to place the doc in.
        workspace_id: ID of the workspace to place the doc in.
        initial_page: Configuration for the initial page of the doc.
            Can include name, subtitle, iconName, imageUrl, parentPageId, and pageContent.

    Returns:
        Dictionary containing information about the newly created doc.
    """
    request = DocCreate(
        title=title,
        source_doc=source_doc,
        timezone=timezone,
        folder_id=folder_id,
        initial_page=initial_page,
    )
    return await docs.create_doc(client, request)


# ============================================================================
# Page Tools
# ============================================================================


@mcp.tool(
    description="List all pages in a Coda doc with pagination support"
)
async def list_pages(
    doc_id: str,
    limit: int | None = None,
    page_token: str | None = None,
) -> PageList:
    """List pages in a Coda doc."""
    return await pages.list_pages(client, doc_id, limit, page_token)


@mcp.tool(
    description="Get detailed metadata about a specific page by its ID or name"
)
async def get_page(doc_id: str, page_id_or_name: str) -> Page:
    """Get details about a page."""
    return await pages.get_page(client, doc_id, page_id_or_name)


@mcp.tool(
    description=(
        "Update properties and content of a page including name, subtitle, icon, "
        "visibility, and HTML/markdown content"
    )
)
async def update_page(
    doc_id: str,
    page_id_or_name: str,
    name: str | None = None,
    subtitle: str | None = None,
    icon_name: str | None = None,
    image_url: str | None = None,
    is_hidden: bool | None = None,
    content_update: PageContentUpdate | None = None,
) -> PageUpdateResult:
    """Update properties of a page.

    Args:
        doc_id: The ID of the doc.
        page_id_or_name: The ID or name of the page.
        name: Name of the page.
        subtitle: Subtitle of the page.
        icon_name: Name of the icon.
        image_url: URL of the cover image.
        is_hidden: Whether the page is hidden.
        content_update: Content update payload, e.g.:
            {
                "insertionMode": "append",
                "canvasContent": {
                    "format": "html",
                    "content": "<p><b>This</b> is rich text</p>"
                }
            }

    Returns:
        API response from Coda.
    """
    page_update = PageUpdate(
        name=name,
        subtitle=subtitle,
        icon_name=icon_name,
        image_url=image_url,
        is_hidden=is_hidden,
        content_update=content_update,
    )
    return await pages.update_page(client, doc_id, page_id_or_name, page_update)


@mcp.tool(
    description="Delete a page from a Coda doc by its ID or name"
)
async def delete_page(doc_id: str, page_id_or_name: str) -> PageDeleteResult:
    """Delete a page from a doc."""
    return await pages.delete_page(client, doc_id, page_id_or_name)


@mcp.tool(
    description=(
        "Start an async export of page content in HTML or markdown format - "
        "returns request ID to poll for completion with get_page_content_export_status"
    )
)
async def begin_page_content_export(
    doc_id: str, page_id_or_name: str, output_format: str = "html"
) -> BeginPageContentExportResponse:
    """Initiate an export of page content.

    This starts an asynchronous export process. The export is not immediate - you must poll
    the status using get_page_content_export_status with the returned request ID.

    IMPORTANT: Due to Coda's server replication, the export request may not be immediately
    available on all servers. If you get a 404 error when checking status, wait 2-3 seconds
    and retry with exponential backoff.

    Workflow:
    1. Call this endpoint to start export
    2. Wait 2-3 seconds for server replication
    3. Poll get_page_content_export_status until status="complete"
    4. Use the downloadLink from the status response to download content

    Args:
        doc_id: ID of the doc.
        page_id_or_name: ID or name of the page.
        output_format: Format for export - either "html" or "markdown".

    Returns:
        Export response with:
        - id: The request ID to use for polling status
        - status: Initial status (usually "inProgress")
        - href: URL to check export status
    """
    export_request = BeginPageContentExportRequest(output_format=output_format)  # type: ignore
    return await pages.begin_page_content_export(client, doc_id, page_id_or_name, export_request)


@mcp.tool(
    description=(
        "Check status of a page export and auto-download content when ready - "
        "poll this after starting export with begin_page_content_export"
    )
)
async def get_page_content_export_status(
    doc_id: str, page_id_or_name: str, request_id: str
) -> PageContentExportStatusResponse:
    """Check the status of a page content export.

    Poll this endpoint to check if your export (initiated with begin_page_content_export) is ready.

    IMPORTANT: 404 errors are expected initially due to server replication lag. If you receive
    a 404 error, wait 2-3 seconds and retry. Use exponential backoff for subsequent retries.

    When the export completes, this function automatically downloads the content for you,
    so you receive the actual page content directly without needing to make an additional request.

    Args:
        doc_id: ID of the doc.
        page_id_or_name: ID or name of the page.
        request_id: The request ID returned from begin_page_content_export.

    Returns:
        Status response with:
        - id: The request ID
        - status: "inProgress", "complete", or "failed"
        - href: URL to check status again
        - downloadLink: (when status="complete") Temporary URL where content was downloaded from
        - content: (when status="complete") The actual exported page content (HTML or markdown)
        - error: (when status="failed") Error message describing what went wrong

    Next steps:
    - If status="inProgress": Wait 1-2 seconds and poll again
    - If status="complete": The content field contains the exported page content
    - If status="failed": Check error message and handle accordingly
    """
    return await pages.get_page_content_export_status(client, doc_id, page_id_or_name, request_id)


@mcp.tool(
    description=(
        "Create a new page in a Coda doc with optional subtitle, icon, parent page, "
        "and initial HTML/markdown content"
    )
)
async def create_page(
    doc_id: str,
    name: str,
    subtitle: str | None = None,
    icon_name: str | None = None,
    image_url: str | None = None,
    parent_page_id: str | None = None,
    page_content: PageContent | None = None,
) -> PageCreateResult:
    """Create a new page in a doc.

    Args:
        doc_id: The ID of the doc.
        name: Name of the page.
        subtitle: Subtitle of the page.
        icon_name: Name of the icon.
        image_url: URL of the cover image.
        parent_page_id: The ID of this new page's parent, if creating a subpage.
        page_content: Content to initialize the page with (rich text or embed), e.g.:
            {
                "type": "canvas",
                "canvasContent": {
                    "format": "html",
                    "content": "<p><b>This</b> is rich text</p>"
                }
            }

    Returns:
        API response from Coda.
    """
    page_create = PageCreate(
        name=name,
        subtitle=subtitle,
        icon_name=icon_name,
        image_url=image_url,
        parent_page_id=parent_page_id,
        page_content=page_content,
    )
    return await pages.create_page(client, doc_id, page_create)


# ============================================================================
# Table Tools
# ============================================================================


@mcp.tool(
    description="List all tables and views in a Coda doc with optional filtering and sorting"
)
async def list_tables(
    doc_id: str,
    limit: int | None = None,
    page_token: str | None = None,
    sort_by: Literal["name"] | None = None,
    table_types: list[str] | None = None,
) -> TableList:
    """List tables in a Coda doc.

    Args:
        doc_id: ID of the doc.
        limit: Maximum number of results to return.
        page_token: An opaque token to fetch the next page of results.
        sort_by: How to sort the results (e.g., 'name').
        table_types: Types of tables to include (e.g., ['table', 'view']).

    Returns:
        List of tables with their metadata.
    """
    return await tables.list_tables(client, doc_id, limit, page_token, sort_by, table_types)


@mcp.tool(
    description="Get detailed information about a specific table including its schema, columns, and metadata"
)
async def get_table(doc_id: str, table_id_or_name: str) -> Table:
    """Get details about a specific table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.

    Returns:
        Table details including columns and metadata.
    """
    return await tables.get_table(client, doc_id, table_id_or_name)


@mcp.tool(
    description="List all columns in a table with their properties, formats, and formulas"
)
async def list_columns(
    doc_id: str,
    table_id_or_name: str,
    limit: int | None = None,
    page_token: str | None = None,
    visible_only: bool | None = None,
) -> ColumnList:
    """List columns in a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        limit: Maximum number of results to return.
        page_token: An opaque token to fetch the next page of results.
        visible_only: If true, only return visible columns.

    Returns:
        List of columns with their properties.
    """
    return await tables.list_columns(client, doc_id, table_id_or_name, limit, page_token, visible_only)


@mcp.tool(
    description="Get detailed information about a specific column including its type, format, and formula"
)
async def get_column(doc_id: str, table_id_or_name: str, column_id_or_name: str) -> Column:
    """Get details about a specific column.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        column_id_or_name: ID or name of the column.

    Returns:
        Column details including format and formula.
    """
    return await tables.get_column(client, doc_id, table_id_or_name, column_id_or_name)


@mcp.tool(
    description="Push a button in a specific table cell to trigger its action"
)
async def push_button(
    doc_id: str,
    table_id_or_name: str,
    row_id_or_name: str,
    column_id_or_name: str,
) -> PushButtonResult:
    """Push a button in a table cell.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID of the table.
        row_id_or_name: ID of the row containing the button.
        column_id_or_name: ID of the column containing the button.

    Returns:
        Result of the button push operation.
    """
    return await tables.push_button(client, doc_id, table_id_or_name, row_id_or_name, column_id_or_name)


# ============================================================================
# Row Tools
# ============================================================================


@mcp.tool(
    description=(
        "List rows in a table with optional filtering, sorting, and pagination - "
        "returns row data with cell values"
    )
)
async def list_rows(
    doc_id: str,
    table_id_or_name: str,
    query: str | None = None,
    sort_by: str | None = None,
    use_column_names: bool | None = None,
    value_format: Literal["simple", "simpleWithArrays", "rich"] | None = None,
    visible_only: bool | None = None,
    limit: int | None = None,
    page_token: str | None = None,
    sync_token: str | None = None,
) -> RowList:
    """List rows in a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        query: Query to filter rows (e.g., 'Status="Complete"').
        sort_by: Column to sort by. Use 'natural' for the table's sort order.
        use_column_names: Use column names instead of IDs in the response.
        value_format: Format for cell values (simple, simpleWithArrays, or rich).
        visible_only: If true, only return visible rows.
        limit: Maximum number of results to return.
        page_token: An opaque token to fetch the next page of results.
        sync_token: Token for incremental sync of changes.

    Returns:
        List of rows with their values.
    """
    return await rows.list_rows(
        client,
        doc_id,
        table_id_or_name,
        query,
        sort_by,
        use_column_names,
        value_format,
        visible_only,
        limit,
        page_token,
        sync_token,
    )


@mcp.tool(
    description="Get a specific row from a table by its ID or name with all cell values"
)
async def get_row(
    doc_id: str,
    table_id_or_name: str,
    row_id_or_name: str,
    use_column_names: bool | None = None,
    value_format: Literal["simple", "simpleWithArrays", "rich"] | None = None,
) -> Row:
    """Get a specific row from a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_id_or_name: ID or name of the row.
        use_column_names: Use column names instead of IDs in the response.
        value_format: Format for cell values (simple, simpleWithArrays, or rich).

    Returns:
        Row data with values.
    """
    return await rows.get_row(client, doc_id, table_id_or_name, row_id_or_name, use_column_names, value_format)


@mcp.tool(
    description="Insert new rows or update existing rows in a table based on key columns - ideal for bulk operations"
)
async def upsert_rows(
    doc_id: str,
    table_id_or_name: str,
    rows_data: list[RowEdit],
    key_columns: list[str] | None = None,
    disable_parsing: bool | None = None,
) -> RowsUpsertResult:
    """Insert or update rows in a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        rows_data: List of rows to upsert. Each row should have a 'cells' array with column/value pairs.
        key_columns: Column IDs/names to use as keys for matching existing rows.
        disable_parsing: If true, cell values won't be parsed (e.g., URLs won't become links).

    Returns:
        Result of the upsert operation.
    """
    return await rows.upsert_rows(client, doc_id, table_id_or_name, rows_data, key_columns, disable_parsing)


@mcp.tool(
    description="Update cell values in a specific row by its ID or name"
)
async def update_row(
    doc_id: str,
    table_id_or_name: str,
    row_id_or_name: str,
    row: RowEdit,
    disable_parsing: bool | None = None,
) -> RowUpdateResult:
    """Update a specific row in a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_id_or_name: ID or name of the row to update.
        row: Row data with cells array containing column/value pairs.
        disable_parsing: If true, cell values won't be parsed.

    Returns:
        Updated row data.
    """
    return await rows.update_row(client, doc_id, table_id_or_name, row_id_or_name, row, disable_parsing)


@mcp.tool(
    description="Delete a specific row from a table by its ID or name"
)
async def delete_row(doc_id: str, table_id_or_name: str, row_id_or_name: str) -> RowDeleteResult:
    """Delete a specific row from a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_id_or_name: ID or name of the row to delete.

    Returns:
        Result of the deletion.
    """
    return await rows.delete_row(client, doc_id, table_id_or_name, row_id_or_name)


@mcp.tool(
    description="Delete multiple rows from a table at once using a list of row IDs"
)
async def delete_rows(
    doc_id: str,
    table_id_or_name: str,
    row_ids: list[str],
) -> RowsDeleteResult:
    """Delete multiple rows from a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_ids: List of row IDs to delete.

    Returns:
        Result of the deletion operation.
    """
    return await rows.delete_rows(client, doc_id, table_id_or_name, row_ids)


# ============================================================================
# Formula Tools
# ============================================================================


@mcp.tool(
    description="List all named formulas in a Coda doc with their names and IDs"
)
async def list_formulas(
    doc_id: str,
    limit: int | None = None,
    page_token: str | None = None,
    sort_by: Literal["name"] | None = None,
) -> Any:
    """List named formulas in a doc.

    Args:
        doc_id: ID of the doc.
        limit: Maximum number of results to return.
        page_token: An opaque token to fetch the next page of results.
        sort_by: How to sort the results.

    Returns:
        List of named formulas.
    """
    return await formulas.list_formulas(client, doc_id, limit, page_token, sort_by)


@mcp.tool(
    description="Get details about a specific named formula including its expression and definition"
)
async def get_formula(doc_id: str, formula_id_or_name: str) -> Any:
    """Get details about a specific formula.

    Args:
        doc_id: ID of the doc.
        formula_id_or_name: ID or name of the formula.

    Returns:
        Formula details including the formula expression.
    """
    return await formulas.get_formula(client, doc_id, formula_id_or_name)


# ============================================================================
# Server Entry Point
# ============================================================================


def main() -> None:
    """Run the server."""
    load_dotenv()
    mcp.run()


if __name__ == "__main__":
    main()
