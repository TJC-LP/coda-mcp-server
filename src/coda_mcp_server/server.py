"""A template MCP server."""

import os
from enum import StrEnum
from typing import Any, Literal, TypedDict

import aiohttp
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


def clean_params(params: dict[str, Any]) -> dict[str, Any]:
    """Clean parameters by removing `None` values."""
    return {k: v for k, v in params.items() if v is not None}


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
            async with session.request(method, url, headers=self.headers, **kwargs) as response:
                response.raise_for_status()
                return await response.json()


mcp = FastMCP("coda", dependencies=["aiohttp"])
client = CodaClient()


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
    """Get info about a particular doc."""
    params = {"title": title, "iconName": iconName}
    return await client.request(Method.GET, f"docs/{docId}", params=clean_params(params))


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


@mcp.tool()
async def updatePage(
    docId: str,
    pageIdOrName: str,
    name: str | None = None,
    subtitle: str | None = None,
    iconName: str | None = None,
    imageUrl: str | None = None,
    isHidden: bool | None = None,
    contentUpdate: dict[str, Any] | None = None,
) -> Any:
    """Update properties of a page."""
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


@mcp.tool()
async def beginPageContentExport(
    docId: str,
    pageIdOrName: str,
    outputFormat: str = "html",
) -> Any:
    """Initiate an export of content for the given page."""
    data = {"outputFormat": outputFormat}
    return await client.request(Method.POST, f"docs/{docId}/pages/{pageIdOrName}/export", json=data)


@mcp.tool()
async def getPageContentExportStatus(
    docId: str,
    pageIdOrName: str,
    requestId: str,
) -> Any:
    """Check the status of a page content export."""
    return await client.request(Method.GET, f"docs/{docId}/pages/{pageIdOrName}/export/{requestId}")


def main() -> None:
    """Run the server."""
    load_dotenv()
    mcp.run()


if __name__ == "__main__":
    main()
