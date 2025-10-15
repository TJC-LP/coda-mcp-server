"""Doc-related MCP tools for Coda API."""

from typing import Any, Literal
from typing_extensions import TypedDict

from ..client import CodaClient, clean_params
from ..models import Method


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


async def whoami(client: CodaClient) -> Any:
    """Get information about the current authenticated user.

    Returns:
        User information including name, email, and scoped token info.
    """
    return await client.request(Method.GET, "whoami")


async def get_doc_info(client: CodaClient, doc_id: str) -> Any:
    """Get info about a particular doc."""
    return await client.request(Method.GET, f"docs/{doc_id}")


async def delete_doc(client: CodaClient, doc_id: str) -> Any:
    """Delete a doc. USE WITH CAUTION."""
    return await client.request(Method.DELETE, f"docs/{doc_id}")


async def update_doc(client: CodaClient, doc_id: str, title: str | None = None, icon_name: str | None = None) -> Any:
    """Update properties of a doc."""
    data = {"title": title, "iconName": icon_name}
    return await client.request(Method.PATCH, f"docs/{doc_id}", json=clean_params(data))


async def list_docs(
    client: CodaClient,
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


async def create_doc(
    client: CodaClient,
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
