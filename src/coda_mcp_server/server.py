"""A template MCP server."""

import asyncio
import json
import os
from enum import StrEnum
from typing import Any, Literal, cast

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

    def __init__(self, apiToken: str | None = None):
        """Initialize the client."""
        self.apiToken = os.getenv("CODA_API_KEY", apiToken)
        self.baseUrl = "https://coda.io/apis/v1"
        self.headers = {"Authorization": f"Bearer {self.apiToken}", "Content-Type": "application/json"}

    async def request(self, method: Method, endpoint: str, **kwargs: Any) -> Any:
        """Make an authenticated request to Coda API."""
        url = f"{self.baseUrl}/{endpoint}"
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
async def getDocInfo(docId: str) -> Any:
    """Get info about a particular doc."""
    return await client.request(Method.GET, f"docs/{docId}")


@mcp.tool()
async def deleteDoc(docId: str) -> Any:
    """Delete a doc. USE WITH CAUTION."""
    return await client.request(Method.DELETE, f"docs/{docId}")


@mcp.tool()
async def updateDoc(docId: str, title: str | None = None, iconName: str | None = None) -> Any:
    """Update properties of a doc."""
    data = {"title": title, "iconName": iconName}
    return await client.request(Method.PATCH, f"docs/{docId}", json=clean_params(data))


@mcp.tool()
async def listDocs(
    isOwner: bool,
    isPublished: bool,
    query: str,
    sourceDoc: str | None = None,
    isStarred: bool | None = None,
    inGallery: bool | None = None,
    workspaceId: str | None = None,
    folderId: str | None = None,
    limit: int | None = None,
    pageToken: str | None = None,
) -> Any:
    """List available docs.

    Returns a list of Coda docs accessible by the user, and which they have opened at least once.
    These are returned in the same order as on the docs page: reverse chronological by the latest
    event relevant to the user (last viewed, edited, or shared).

    Args:
        isOwner: Show only docs owned by the user.
        isPublished: Show only published docs.
        query: Search term used to filter down results.
        sourceDoc: Show only docs copied from the specified doc ID.
        isStarred: If true, returns docs that are starred. If false, returns docs that are not starred.
        inGallery: Show only docs visible within the gallery.
        workspaceId: Show only docs belonging to the given workspace.
        folderId: Show only docs belonging to the given folder.
        limit: Maximum number of results to return in this query (default: 25).
        pageToken: An opaque token used to fetch the next page of results.

    Returns:
        Dictionary containing document list and pagination info.
    """
    params = {
        "isOwner": str(isOwner).lower(),  # Convert to "true" or "false"
        "isPublished": str(isPublished).lower(),
        "query": query,
        "sourceDoc": sourceDoc,
        "isStarred": str(isStarred).lower() if isStarred is not None else None,
        "inGallery": str(inGallery).lower() if inGallery is not None else None,
        "workspaceId": workspaceId,
        "folderId": folderId,
        "limit": limit,
        "pageToken": pageToken,
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
async def createDoc(
    title: str,
    sourceDoc: str | None = None,
    timezone: str | None = None,
    folderId: str | None = None,
    workspaceId: str | None = None,
    initialPage: InitialPage | None = None,
) -> Any:
    """Create a new Coda doc.

    Args:
        title: Title of the new doc.
        sourceDoc: Optional ID of a doc to copy.
        timezone: Timezone for the doc, e.g. 'America/Los_Angeles'.
        folderId: ID of the folder to place the doc in.
        workspaceId: ID of the workspace to place the doc in.
        initialPage: Configuration for the initial page of the doc.
            Can include name, subtitle, iconName, imageUrl, parentPageId, and pageContent.

    Returns:
        Dictionary containing information about the newly created doc.
    """
    request_data: dict[str, Any] = {"title": title}

    if sourceDoc:
        request_data["sourceDoc"] = sourceDoc
    if timezone:
        request_data["timezone"] = timezone
    if folderId:
        request_data["folderId"] = folderId
    if workspaceId:
        request_data["workspaceId"] = workspaceId
    if initialPage:
        request_data["initialPage"] = initialPage

    return await client.request(Method.POST, "docs", json=request_data)


@mcp.tool()
async def listPages(
    docId: str,
    limit: int | None = None,
    pageToken: str | None = None,
) -> Any:
    """List pages in a Coda doc."""
    params = {
        "limit": limit,
        "pageToken": pageToken,
    }
    return await client.request(Method.GET, f"docs/{docId}/pages", params=clean_params(params))


@mcp.tool()
async def getPage(docId: str, pageIdOrName: str) -> Any:
    """Get details about a page."""
    return await client.request(Method.GET, f"docs/{docId}/pages/{pageIdOrName}")


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
async def updatePage(
    docId: str,
    pageIdOrName: str,
    name: str | None = None,
    subtitle: str | None = None,
    iconName: str | None = None,
    imageUrl: str | None = None,
    isHidden: bool | None = None,
    contentUpdate: PageContentUpdate | None = None,
) -> Any:
    """Update properties of a page.

    Args:
        docId: The ID of the doc.
        pageIdOrName: The ID or name of the page.
        name: Name of the page.
        subtitle: Subtitle of the page.
        iconName: Name of the icon.
        imageUrl: URL of the cover image.
        isHidden: Whether the page is hidden.
        contentUpdate: Content update payload, e.g.:
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
    if iconName is not None:
        data["iconName"] = iconName
    if imageUrl is not None:
        data["imageUrl"] = imageUrl
    if isHidden is not None:
        data["isHidden"] = isHidden
    if contentUpdate is not None:
        data["contentUpdate"] = contentUpdate
    return await client.request(Method.PUT, f"docs/{docId}/pages/{pageIdOrName}", json=data)


@mcp.tool()
async def deletePage(docId: str, pageIdOrName: str) -> Any:
    """Delete a page from a doc."""
    return await client.request(Method.DELETE, f"docs/{docId}/pages/{pageIdOrName}")


# Note: beginPageContentExport and getPageContentExportStatus have been removed
# in favor of the simpler getPageContent function that handles the entire workflow


# Internal helper functions (not exposed as MCP tools)
async def _begin_page_export(docId: str, pageIdOrName: str, outputFormat: str = "html") -> dict[str, Any]:
    """Internal function to start a page content export."""
    data = {"outputFormat": outputFormat}
    result = await client.request(Method.POST, f"docs/{docId}/pages/{pageIdOrName}/export", json=data)
    return cast(dict[str, Any], result)


async def _get_export_status(docId: str, pageIdOrName: str, requestId: str) -> dict[str, Any]:
    """Internal function to check page export status."""
    result = await client.request(Method.GET, f"docs/{docId}/pages/{pageIdOrName}/export/{requestId}")
    return cast(dict[str, Any], result)


async def _get_export_status_by_href(href: str) -> dict[str, Any]:
    """Internal function to check page export status using the href from the export response."""
    # Extract the path from the full URL
    # href format: https://coda.io/apis/v1/docs/{docId}/pages/{pageId}/export/{requestId}
    if href.startswith(client.baseUrl):
        path = href[len(client.baseUrl) + 1 :]  # +1 for the trailing slash
    else:
        # Handle case where href might be a full URL with different base
        import urllib.parse

        parsed = urllib.parse.urlparse(href)
        path = parsed.path.replace("/apis/v1/", "", 1)

    result = await client.request(Method.GET, path)
    return cast(dict[str, Any], result)


async def _download_content(url: str) -> str:
    """Internal function to download content from a URL."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
            return content


@mcp.tool()
async def getPageContent(docId: str, pageIdOrName: str, outputFormat: str = "html") -> Any:
    """Export and retrieve page content (convenience method).

    This method combines beginPageContentExport and getPageContentExportStatus
    to provide a simple way to get page content. It handles the polling loop
    and returns the actual content.

    Args:
        docId: ID of the doc.
        pageIdOrName: ID or name of the page.
        outputFormat: Format for export (html or markdown).

    Returns:
        The exported page content as a string.
    """
    # Start export using internal function
    try:
        export_result = await _begin_page_export(docId, pageIdOrName, outputFormat)
    except Exception as e:
        raise Exception(f"Failed to start page export: {str(e)}")

    request_id = export_result.get("id")
    href = export_result.get("href")

    if not request_id:
        raise Exception(f"Failed to start export - no request ID returned. Response: {export_result}")

    if not href:
        raise Exception(f"Failed to start export - no href returned. Response: {export_result}")

    # Poll for completion (with timeout)
    max_attempts = 30
    for i in range(max_attempts):
        # Use the href from the export response to check status
        status = await _get_export_status_by_href(href)

        if status.get("status") == "complete":
            # Fetch content from download URL
            download_url = status.get("downloadLink")
            if download_url:
                return await _download_content(download_url)
            else:
                raise Exception("Export completed but no download URL provided")

        elif status.get("status") == "failed":
            error = status.get("error", "Unknown error")
            raise Exception(f"Export failed: {error}")

        # Wait before next poll
        await asyncio.sleep(1)

    raise Exception("Export timed out after 30 seconds")


@mcp.tool()
async def createPage(
    docId: str,
    name: str,
    subtitle: str | None = None,
    iconName: str | None = None,
    imageUrl: str | None = None,
    parentPageId: str | None = None,
    pageContent: PageContent | None = None,
) -> Any:
    """Create a new page in a doc.

    Args:
        docId: The ID of the doc.
        name: Name of the page.
        subtitle: Subtitle of the page.
        iconName: Name of the icon.
        imageUrl: URL of the cover image.
        parentPageId: The ID of this new page's parent, if creating a subpage.
        pageContent: Content to initialize the page with (rich text or embed), e.g.:
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
    if iconName is not None:
        data["iconName"] = iconName
    if imageUrl is not None:
        data["imageUrl"] = imageUrl
    if parentPageId is not None:
        data["parentPageId"] = parentPageId
    if pageContent is not None:
        data["pageContent"] = pageContent

    return await client.request(Method.POST, f"docs/{docId}/pages", json=data)


@mcp.tool()
async def listTables(
    docId: str,
    limit: int | None = None,
    pageToken: str | None = None,
    sortBy: Literal["name"] | None = None,
    tableTypes: list[str] | None = None,
) -> Any:
    """List tables in a Coda doc.

    Args:
        docId: ID of the doc.
        limit: Maximum number of results to return.
        pageToken: An opaque token to fetch the next page of results.
        sortBy: How to sort the results (e.g., 'name').
        tableTypes: Types of tables to include (e.g., ['table', 'view']).

    Returns:
        List of tables with their metadata.
    """
    params = {
        "limit": limit,
        "pageToken": pageToken,
        "sortBy": sortBy,
        "tableTypes": tableTypes,
    }
    return await client.request(Method.GET, f"docs/{docId}/tables", params=clean_params(params))


@mcp.tool()
async def getTable(docId: str, tableIdOrName: str) -> Any:
    """Get details about a specific table.

    Args:
        docId: ID of the doc.
        tableIdOrName: ID or name of the table.

    Returns:
        Table details including columns and metadata.
    """
    return await client.request(Method.GET, f"docs/{docId}/tables/{tableIdOrName}")


@mcp.tool()
async def listColumns(
    docId: str,
    tableIdOrName: str,
    limit: int | None = None,
    pageToken: str | None = None,
    visibleOnly: bool | None = None,
) -> Any:
    """List columns in a table.

    Args:
        docId: ID of the doc.
        tableIdOrName: ID or name of the table.
        limit: Maximum number of results to return.
        pageToken: An opaque token to fetch the next page of results.
        visibleOnly: If true, only return visible columns.

    Returns:
        List of columns with their properties.
    """
    params = {
        "limit": limit,
        "pageToken": pageToken,
        "visibleOnly": visibleOnly,
    }
    return await client.request(Method.GET, f"docs/{docId}/tables/{tableIdOrName}/columns", params=clean_params(params))


@mcp.tool()
async def getColumn(docId: str, tableIdOrName: str, columnIdOrName: str) -> Any:
    """Get details about a specific column.

    Args:
        docId: ID of the doc.
        tableIdOrName: ID or name of the table.
        columnIdOrName: ID or name of the column.

    Returns:
        Column details including format and formula.
    """
    return await client.request(Method.GET, f"docs/{docId}/tables/{tableIdOrName}/columns/{columnIdOrName}")


@mcp.tool()
async def listRows(
    docId: str,
    tableIdOrName: str,
    query: str | None = None,
    sortBy: str | None = None,
    useColumnNames: bool | None = None,
    valueFormat: Literal["simple", "simpleWithArrays", "rich"] | None = None,
    visibleOnly: bool | None = None,
    limit: int | None = None,
    pageToken: str | None = None,
    syncToken: str | None = None,
) -> Any:
    """List rows in a table.

    Args:
        docId: ID of the doc.
        tableIdOrName: ID or name of the table.
        query: Query to filter rows (e.g., 'Status="Complete"').
        sortBy: Column to sort by. Use 'natural' for the table's sort order.
        useColumnNames: Use column names instead of IDs in the response.
        valueFormat: Format for cell values (simple, simpleWithArrays, or rich).
        visibleOnly: If true, only return visible rows.
        limit: Maximum number of results to return.
        pageToken: An opaque token to fetch the next page of results.
        syncToken: Token for incremental sync of changes.

    Returns:
        List of rows with their values.
    """
    params = {
        "query": query,
        "sortBy": sortBy,
        "useColumnNames": useColumnNames,
        "valueFormat": valueFormat,
        "visibleOnly": visibleOnly,
        "limit": limit,
        "pageToken": pageToken,
        "syncToken": syncToken,
    }
    return await client.request(Method.GET, f"docs/{docId}/tables/{tableIdOrName}/rows", params=clean_params(params))


@mcp.tool()
async def getRow(
    docId: str,
    tableIdOrName: str,
    rowIdOrName: str,
    useColumnNames: bool | None = None,
    valueFormat: Literal["simple", "simpleWithArrays", "rich"] | None = None,
) -> Any:
    """Get a specific row from a table.

    Args:
        docId: ID of the doc.
        tableIdOrName: ID or name of the table.
        rowIdOrName: ID or name of the row.
        useColumnNames: Use column names instead of IDs in the response.
        valueFormat: Format for cell values (simple, simpleWithArrays, or rich).

    Returns:
        Row data with values.
    """
    params = {
        "useColumnNames": useColumnNames,
        "valueFormat": valueFormat,
    }
    return await client.request(
        Method.GET, f"docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}", params=clean_params(params)
    )


@mcp.tool()
async def upsertRows(
    docId: str,
    tableIdOrName: str,
    rows: list[RowUpdate],
    keyColumns: list[str] | None = None,
    disableParsing: bool | None = None,
) -> Any:
    """Insert or update rows in a table.

    Args:
        docId: ID of the doc.
        tableIdOrName: ID or name of the table.
        rows: List of rows to upsert. Each row should have a 'cells' array with column/value pairs.
        keyColumns: Column IDs/names to use as keys for matching existing rows.
        disableParsing: If true, cell values won't be parsed (e.g., URLs won't become links).

    Returns:
        Result of the upsert operation.
    """
    data = {
        "rows": rows,
        "keyColumns": keyColumns,
        "disableParsing": disableParsing,
    }
    return await client.request(Method.POST, f"docs/{docId}/tables/{tableIdOrName}/rows", json=clean_params(data))


@mcp.tool()
async def updateRow(
    docId: str,
    tableIdOrName: str,
    rowIdOrName: str,
    row: RowUpdate,
    disableParsing: bool | None = None,
) -> Any:
    """Update a specific row in a table.

    Args:
        docId: ID of the doc.
        tableIdOrName: ID or name of the table.
        rowIdOrName: ID or name of the row to update.
        row: Row data with cells array containing column/value pairs.
        disableParsing: If true, cell values won't be parsed.

    Returns:
        Updated row data.
    """
    data = {
        "row": row,
        "disableParsing": disableParsing,
    }
    return await client.request(
        Method.PUT, f"docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}", json=clean_params(data)
    )


@mcp.tool()
async def deleteRow(docId: str, tableIdOrName: str, rowIdOrName: str) -> Any:
    """Delete a specific row from a table.

    Args:
        docId: ID of the doc.
        tableIdOrName: ID or name of the table.
        rowIdOrName: ID or name of the row to delete.

    Returns:
        Result of the deletion.
    """
    return await client.request(Method.DELETE, f"docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}")


@mcp.tool()
async def deleteRows(
    docId: str,
    tableIdOrName: str,
    rowIds: list[str],
) -> Any:
    """Delete multiple rows from a table.

    Args:
        docId: ID of the doc.
        tableIdOrName: ID or name of the table.
        rowIds: List of row IDs to delete.

    Returns:
        Result of the deletion operation.
    """
    data = {"rowIds": rowIds}
    return await client.request(Method.DELETE, f"docs/{docId}/tables/{tableIdOrName}/rows", json=data)


@mcp.tool()
async def pushButton(
    docId: str,
    tableIdOrName: str,
    rowIdOrName: str,
    columnIdOrName: str,
) -> Any:
    """Push a button in a table cell.

    Args:
        docId: ID of the doc.
        tableIdOrName: ID or name of the table.
        rowIdOrName: ID or name of the row containing the button.
        columnIdOrName: ID or name of the column containing the button.

    Returns:
        Result of the button push operation.
    """
    return await client.request(
        Method.POST, f"docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}/buttons/{columnIdOrName}", json={}
    )


@mcp.tool()
async def listFormulas(
    docId: str,
    limit: int | None = None,
    pageToken: str | None = None,
    sortBy: Literal["name"] | None = None,
) -> Any:
    """List named formulas in a doc.

    Args:
        docId: ID of the doc.
        limit: Maximum number of results to return.
        pageToken: An opaque token to fetch the next page of results.
        sortBy: How to sort the results.

    Returns:
        List of named formulas.
    """
    params = {"limit": limit, "pageToken": pageToken, "sortBy": sortBy}
    return await client.request(Method.GET, f"docs/{docId}/formulas", params=clean_params(params))


@mcp.tool()
async def getFormula(docId: str, formulaIdOrName: str) -> Any:
    """Get details about a specific formula.

    Args:
        docId: ID of the doc.
        formulaIdOrName: ID or name of the formula.

    Returns:
        Formula details including the formula expression.
    """
    return await client.request(Method.GET, f"docs/{docId}/formulas/{formulaIdOrName}")


def main() -> None:
    """Run the server."""
    load_dotenv()
    mcp.run()


if __name__ == "__main__":
    main()
