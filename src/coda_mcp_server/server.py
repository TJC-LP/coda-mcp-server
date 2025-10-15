"""A template MCP server."""

import json
import os
from enum import StrEnum
from typing import Any, Literal

import aiohttp
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing_extensions import TypedDict


def clean_params(params: dict[str, Any]) -> dict[str, Any]:
    """Clean parameters by removing `None` values and converting booleans to strings."""
    cleaned = {}
    for k, v in params.items():
        if v is not None:
            if isinstance(v, bool):
                cleaned[k] = str(v).lower()  # Convert True -> "true", False -> "false"
            else:
                cleaned[k] = v
    return cleaned


class Method(StrEnum):
    """API methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class CodaClient:
    """MCP server for Coda.io integration."""

    def __init__(self, api_token: str | None = None):
        """Initialize the client."""
        self.api_token = os.getenv("CODA_API_KEY", api_token)
        self.base_url = "https://coda.io/apis/v1"
        self.headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}

    async def request(self, method: Method, endpoint: str, **kwargs: Any) -> Any:
        """Make an authenticated request to Coda API."""
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url, headers=self.headers, **kwargs) as response:
                    if response.status == 429:
                        retry_after = response.headers.get("Retry-After", "60")
                        raise Exception(f"Rate limit exceeded. Retry after {retry_after} seconds.")

                    response_text = await response.text()

                    if not response.ok:
                        error_data = None
                        try:
                            error_data = await response.json()
                        except (json.JSONDecodeError, aiohttp.ContentTypeError):
                            # Response body is not valid JSON, which is expected for some error responses
                            error_data = None

                        error_message = f"API Error {response.status}: {response.reason}"
                        if error_data and isinstance(error_data, dict):
                            if "message" in error_data:
                                error_message = f"API Error {response.status}: {error_data['message']}"
                            elif "error" in error_data:
                                error_message = f"API Error {response.status}: {error_data['error']}"
                        elif response_text:
                            error_message = f"API Error {response.status}: {response_text}"

                        raise Exception(error_message)

                    # Return empty dict for 204 No Content responses
                    if response.status == 204:
                        return {}

                    # Try to parse JSON response
                    try:
                        return json.loads(response_text) if response_text else {}
                    except json.JSONDecodeError:
                        raise Exception(f"Invalid JSON response: {response_text[:200]}")

            except aiohttp.ClientError as e:
                raise Exception(f"Network error: {str(e)}")
            except Exception as e:
                # Re-raise our custom exceptions
                if str(e).startswith(("API Error", "Rate limit", "Invalid JSON", "Network error")):
                    raise
                # Wrap unexpected errors
                raise Exception(f"Unexpected error: {str(e)}")


mcp = FastMCP("coda", dependencies=["aiohttp"])
client = CodaClient()


@mcp.tool()
async def whoami() -> Any:
    """Get information about the current authenticated user.

    Returns:
        User information including name, email, and scoped token info.
    """
    return await client.request(Method.GET, "whoami")


@mcp.tool()
async def get_doc_info(doc_id: str) -> Any:
    """Get info about a particular doc."""
    return await client.request(Method.GET, f"docs/{doc_id}")


@mcp.tool()
async def delete_doc(doc_id: str) -> Any:
    """Delete a doc. USE WITH CAUTION."""
    return await client.request(Method.DELETE, f"docs/{doc_id}")


@mcp.tool()
async def update_doc(doc_id: str, title: str | None = None, icon_name: str | None = None) -> Any:
    """Update properties of a doc."""
    data = {"title": title, "iconName": icon_name}
    return await client.request(Method.PATCH, f"docs/{doc_id}", json=clean_params(data))


@mcp.tool()
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
) -> Any:
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
    params = {
        "isOwner": str(is_owner).lower(),  # Convert to "true" or "false"
        "isPublished": str(is_published).lower(),
        "query": query,
        "sourceDoc": source_doc,
        "isStarred": str(is_starred).lower() if is_starred is not None else None,
        "inGallery": str(in_gallery).lower() if in_gallery is not None else None,
        "workspaceId": workspace_id,
        "folderId": folder_id,
        "limit": limit,
        "pageToken": page_token,
    }
    return await client.request(Method.GET, "docs", params=clean_params(params))


class CanvasContent(TypedDict):
    """Canvas content."""

    format: Literal["html", "markdown"]
    content: str


class PageContent(TypedDict):
    """Page content."""

    type: Literal["canvas"]
    canvasContent: CanvasContent


class InitialPage(TypedDict, total=False):
    """Initial page."""

    name: str
    subtitle: str
    iconName: str
    imageUrl: str
    parentPageId: str
    pageContent: PageContent


@mcp.tool()
async def create_doc(
    title: str,
    source_doc: str | None = None,
    timezone: str | None = None,
    folder_id: str | None = None,
    workspace_id: str | None = None,
    initial_page: InitialPage | None = None,
) -> Any:
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
    request_data: dict[str, Any] = {"title": title}

    if source_doc:
        request_data["sourceDoc"] = source_doc
    if timezone:
        request_data["timezone"] = timezone
    if folder_id:
        request_data["folderId"] = folder_id
    if workspace_id:
        request_data["workspaceId"] = workspace_id
    if initial_page:
        request_data["initialPage"] = initial_page

    return await client.request(Method.POST, "docs", json=request_data)


@mcp.tool()
async def list_pages(
    doc_id: str,
    limit: int | None = None,
    page_token: str | None = None,
) -> Any:
    """List pages in a Coda doc."""
    params = {
        "limit": limit,
        "pageToken": page_token,
    }
    return await client.request(Method.GET, f"docs/{doc_id}/pages", params=clean_params(params))


@mcp.tool()
async def get_page(doc_id: str, page_id_or_name: str) -> Any:
    """Get details about a page."""
    return await client.request(Method.GET, f"docs/{doc_id}/pages/{page_id_or_name}")


class PageContentUpdate(TypedDict):
    """Page content update."""

    insertionMode: Literal["append", "replace"]
    canvasContent: CanvasContent


class CellValue(TypedDict, total=False):
    """Cell value for row operations."""

    column: str  # Column ID or name
    value: Any  # The value to set


class RowUpdate(TypedDict, total=False):
    """Row data for upsert/update operations."""

    cells: list[CellValue]  # Cell values to update


@mcp.tool()
async def update_page(
    doc_id: str,
    page_id_or_name: str,
    name: str | None = None,
    subtitle: str | None = None,
    icon_name: str | None = None,
    image_url: str | None = None,
    is_hidden: bool | None = None,
    content_update: PageContentUpdate | None = None,
) -> Any:
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
    data: dict[str, Any] = {}
    if name is not None:
        data["name"] = name
    if subtitle is not None:
        data["subtitle"] = subtitle
    if icon_name is not None:
        data["iconName"] = icon_name
    if image_url is not None:
        data["imageUrl"] = image_url
    if is_hidden is not None:
        data["isHidden"] = is_hidden
    if content_update is not None:
        data["contentUpdate"] = content_update
    return await client.request(Method.PUT, f"docs/{doc_id}/pages/{page_id_or_name}", json=data)


@mcp.tool()
async def delete_page(doc_id: str, page_id_or_name: str) -> Any:
    """Delete a page from a doc."""
    return await client.request(Method.DELETE, f"docs/{doc_id}/pages/{page_id_or_name}")


# Page content export endpoints - expose async workflow to LLM for better error handling
# The LLM will handle the multi-step process: initiate export, poll status, download content


@mcp.tool()
async def begin_page_content_export(doc_id: str, page_id_or_name: str, output_format: str = "html") -> Any:
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
    data = {"outputFormat": output_format}
    result = await client.request(Method.POST, f"docs/{doc_id}/pages/{page_id_or_name}/export", json=data)
    return result


@mcp.tool()
async def get_page_content_export_status(doc_id: str, page_id_or_name: str, request_id: str) -> Any:
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
    result = await client.request(Method.GET, f"docs/{doc_id}/pages/{page_id_or_name}/export/{request_id}")

    # Auto-fetch content when export is complete
    if result.get("status") == "complete" and result.get("downloadLink"):
        download_url = result["downloadLink"]
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                result["content"] = await response.text()

    return result


@mcp.tool()
async def create_page(
    doc_id: str,
    name: str,
    subtitle: str | None = None,
    icon_name: str | None = None,
    image_url: str | None = None,
    parent_page_id: str | None = None,
    page_content: PageContent | None = None,
) -> Any:
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
    data: dict[str, Any] = {"name": name}
    if subtitle is not None:
        data["subtitle"] = subtitle
    if icon_name is not None:
        data["iconName"] = icon_name
    if image_url is not None:
        data["imageUrl"] = image_url
    if parent_page_id is not None:
        data["parentPageId"] = parent_page_id
    if page_content is not None:
        data["pageContent"] = page_content

    return await client.request(Method.POST, f"docs/{doc_id}/pages", json=data)


@mcp.tool()
async def list_tables(
    doc_id: str,
    limit: int | None = None,
    page_token: str | None = None,
    sort_by: Literal["name"] | None = None,
    table_types: list[str] | None = None,
) -> Any:
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
    params = {
        "limit": limit,
        "pageToken": page_token,
        "sortBy": sort_by,
        "tableTypes": table_types,
    }
    return await client.request(Method.GET, f"docs/{doc_id}/tables", params=clean_params(params))


@mcp.tool()
async def get_table(doc_id: str, table_id_or_name: str) -> Any:
    """Get details about a specific table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.

    Returns:
        Table details including columns and metadata.
    """
    return await client.request(Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}")


@mcp.tool()
async def list_columns(
    doc_id: str,
    table_id_or_name: str,
    limit: int | None = None,
    page_token: str | None = None,
    visible_only: bool | None = None,
) -> Any:
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
    params = {
        "limit": limit,
        "pageToken": page_token,
        "visibleOnly": visible_only,
    }
    return await client.request(
        Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}/columns", params=clean_params(params)
    )


@mcp.tool()
async def get_column(doc_id: str, table_id_or_name: str, column_id_or_name: str) -> Any:
    """Get details about a specific column.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        column_id_or_name: ID or name of the column.

    Returns:
        Column details including format and formula.
    """
    return await client.request(Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}/columns/{column_id_or_name}")


@mcp.tool()
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
) -> Any:
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
    params = {
        "query": query,
        "sortBy": sort_by,
        "useColumnNames": use_column_names,
        "valueFormat": value_format,
        "visibleOnly": visible_only,
        "limit": limit,
        "pageToken": page_token,
        "syncToken": sync_token,
    }
    return await client.request(
        Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}/rows", params=clean_params(params)
    )


@mcp.tool()
async def get_row(
    doc_id: str,
    table_id_or_name: str,
    row_id_or_name: str,
    use_column_names: bool | None = None,
    value_format: Literal["simple", "simpleWithArrays", "rich"] | None = None,
) -> Any:
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
    params = {
        "useColumnNames": use_column_names,
        "valueFormat": value_format,
    }
    return await client.request(
        Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}", params=clean_params(params)
    )


@mcp.tool()
async def upsert_rows(
    doc_id: str,
    table_id_or_name: str,
    rows: list[RowUpdate],
    key_columns: list[str] | None = None,
    disable_parsing: bool | None = None,
) -> Any:
    """Insert or update rows in a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        rows: List of rows to upsert. Each row should have a 'cells' array with column/value pairs.
        key_columns: Column IDs/names to use as keys for matching existing rows.
        disable_parsing: If true, cell values won't be parsed (e.g., URLs won't become links).

    Returns:
        Result of the upsert operation.
    """
    data = {
        "rows": rows,
        "keyColumns": key_columns,
        "disableParsing": disable_parsing,
    }
    return await client.request(Method.POST, f"docs/{doc_id}/tables/{table_id_or_name}/rows", json=clean_params(data))


@mcp.tool()
async def update_row(
    doc_id: str,
    table_id_or_name: str,
    row_id_or_name: str,
    row: RowUpdate,
    disable_parsing: bool | None = None,
) -> Any:
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
    data = {
        "row": row,
        "disableParsing": disable_parsing,
    }
    return await client.request(
        Method.PUT, f"docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}", json=clean_params(data)
    )


@mcp.tool()
async def delete_row(doc_id: str, table_id_or_name: str, row_id_or_name: str) -> Any:
    """Delete a specific row from a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_id_or_name: ID or name of the row to delete.

    Returns:
        Result of the deletion.
    """
    return await client.request(Method.DELETE, f"docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}")


@mcp.tool()
async def delete_rows(
    doc_id: str,
    table_id_or_name: str,
    row_ids: list[str],
) -> Any:
    """Delete multiple rows from a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_ids: List of row IDs to delete.

    Returns:
        Result of the deletion operation.
    """
    data = {"rowIds": row_ids}
    return await client.request(Method.DELETE, f"docs/{doc_id}/tables/{table_id_or_name}/rows", json=data)


@mcp.tool()
async def push_button(
    doc_id: str,
    table_id_or_name: str,
    row_id_or_name: str,
    column_id_or_name: str,
) -> Any:
    """Push a button in a table cell.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_id_or_name: ID or name of the row containing the button.
        column_id_or_name: ID or name of the column containing the button.

    Returns:
        Result of the button push operation.
    """
    return await client.request(
        Method.POST,
        f"docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}/buttons/{column_id_or_name}",
        json={},
    )


@mcp.tool()
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
    params = {"limit": limit, "pageToken": page_token, "sortBy": sort_by}
    return await client.request(Method.GET, f"docs/{doc_id}/formulas", params=clean_params(params))


@mcp.tool()
async def get_formula(doc_id: str, formula_id_or_name: str) -> Any:
    """Get details about a specific formula.

    Args:
        doc_id: ID of the doc.
        formula_id_or_name: ID or name of the formula.

    Returns:
        Formula details including the formula expression.
    """
    return await client.request(Method.GET, f"docs/{doc_id}/formulas/{formula_id_or_name}")


def main() -> None:
    """Run the server."""
    load_dotenv()
    mcp.run()


if __name__ == "__main__":
    main()
