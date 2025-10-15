"""Page-related tools for Coda."""

from typing import Any, Literal

import aiohttp
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


class PageContentUpdate(TypedDict):
    """Page content update."""

    insertionMode: Literal["append", "replace"]
    canvasContent: CanvasContent


async def list_pages(
    client: CodaClient,
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


async def get_page(client: CodaClient, doc_id: str, page_id_or_name: str) -> Any:
    """Get details about a page."""
    return await client.request(Method.GET, f"docs/{doc_id}/pages/{page_id_or_name}")


async def update_page(
    client: CodaClient,
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
        client: The Coda client instance.
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


async def delete_page(client: CodaClient, doc_id: str, page_id_or_name: str) -> Any:
    """Delete a page from a doc."""
    return await client.request(Method.DELETE, f"docs/{doc_id}/pages/{page_id_or_name}")


# Page content export endpoints - expose async workflow to LLM for better error handling
# The LLM will handle the multi-step process: initiate export, poll status, download content


async def begin_page_content_export(
    client: CodaClient, doc_id: str, page_id_or_name: str, output_format: str = "html"
) -> Any:
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
        client: The Coda client instance.
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


async def get_page_content_export_status(
    client: CodaClient, doc_id: str, page_id_or_name: str, request_id: str
) -> Any:
    """Check the status of a page content export.

    Poll this endpoint to check if your export (initiated with begin_page_content_export) is ready.

    IMPORTANT: 404 errors are expected initially due to server replication lag. If you receive
    a 404 error, wait 2-3 seconds and retry. Use exponential backoff for subsequent retries.

    When the export completes, this function automatically downloads the content for you,
    so you receive the actual page content directly without needing to make an additional request.

    Args:
        client: The Coda client instance.
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


async def create_page(
    client: CodaClient,
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
        client: The Coda client instance.
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
