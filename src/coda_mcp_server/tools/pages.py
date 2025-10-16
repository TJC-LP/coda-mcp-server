"""Page-related tools for Coda."""

import aiohttp

from ..client import CodaClient, clean_params
from ..models import Method
from ..models.exports import (
    BeginPageContentExportRequest,
    BeginPageContentExportResponse,
    PageContentExportStatusResponse,
)
from ..models.pages import (
    Page,
    PageCreate,
    PageCreateResult,
    PageDeleteResult,
    PageList,
    PageUpdate,
    PageUpdateResult,
)


async def list_pages(
    client: CodaClient,
    doc_id: str,
    limit: int | None = None,
    page_token: str | None = None,
) -> PageList:
    """List pages in a Coda doc."""
    params = {
        "limit": limit,
        "pageToken": page_token,
    }
    result = await client.request(Method.GET, f"docs/{doc_id}/pages", params=clean_params(params))
    return PageList.model_validate(result)


async def get_page(client: CodaClient, doc_id: str, page_id_or_name: str) -> Page:
    """Get details about a page."""
    result = await client.request(Method.GET, f"docs/{doc_id}/pages/{page_id_or_name}")
    return Page.model_validate(result)


async def update_page(
    client: CodaClient,
    doc_id: str,
    page_id_or_name: str,
    page_update: PageUpdate,
) -> PageUpdateResult:
    """Update properties of a page.

    Args:
        client: The Coda client instance.
        doc_id: The ID of the doc.
        page_id_or_name: The ID or name of the page.
        page_update: PageUpdate model with all page update parameters.

    Returns:
        PageUpdateResult with the updated page's metadata.
    """
    result = await client.request(
        Method.PUT,
        f"docs/{doc_id}/pages/{page_id_or_name}",
        json=page_update.model_dump(by_alias=True, exclude_none=True),
    )
    return PageUpdateResult.model_validate(result)


async def delete_page(client: CodaClient, doc_id: str, page_id_or_name: str) -> PageDeleteResult:
    """Delete a page from a doc."""
    result = await client.request(Method.DELETE, f"docs/{doc_id}/pages/{page_id_or_name}")
    return PageDeleteResult.model_validate(result)


# Page content export endpoints - expose async workflow to LLM for better error handling
# The LLM will handle the multi-step process: initiate export, poll status, download content


async def begin_page_content_export(
    client: CodaClient,
    doc_id: str,
    page_id_or_name: str,
    export_request: BeginPageContentExportRequest,
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
        client: The Coda client instance.
        doc_id: ID of the doc.
        page_id_or_name: ID or name of the page.
        export_request: BeginPageContentExportRequest model with output format.

    Returns:
        BeginPageContentExportResponse with:
        - id: The request ID to use for polling status
        - status: Initial status (usually "inProgress")
        - href: URL to check export status
    """
    result = await client.request(
        Method.POST,
        f"docs/{doc_id}/pages/{page_id_or_name}/export",
        json=export_request.model_dump(by_alias=True, exclude_none=True),
    )
    return BeginPageContentExportResponse.model_validate(result)


async def get_page_content_export_status(
    client: CodaClient, doc_id: str, page_id_or_name: str, request_id: str
) -> PageContentExportStatusResponse:
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
        PageContentExportStatusResponse with:
        - id: The request ID
        - status: "inProgress", "complete", or "failed"
        - href: URL to check status again
        - download_link: (when status="complete") Temporary URL where content was downloaded from
        - content: (when status="complete") The actual exported page content (HTML or markdown)
        - error: (when status="failed") Error message describing what went wrong

    Next steps:
    - If status="inProgress": Wait 1-2 seconds and poll again
    - If status="complete": The content field contains the exported page content
    - If status="failed": Check error message and handle accordingly
    """
    result = await client.request(Method.GET, f"docs/{doc_id}/pages/{page_id_or_name}/export/{request_id}")
    response = PageContentExportStatusResponse.model_validate(result)

    # Auto-fetch content when export is complete
    if response.status == "complete" and response.download_link:
        async with aiohttp.ClientSession() as session:
            async with session.get(response.download_link) as http_response:
                response.content = await http_response.text()

    return response


async def create_page(
    client: CodaClient,
    doc_id: str,
    page_create: PageCreate,
) -> PageCreateResult:
    """Create a new page in a doc.

    Args:
        client: The Coda client instance.
        doc_id: The ID of the doc.
        page_create: PageCreate model with all page creation parameters.

    Returns:
        PageCreateResult with the created page's metadata.
    """
    result = await client.request(
        Method.POST,
        f"docs/{doc_id}/pages",
        json=page_create.model_dump(by_alias=True, exclude_none=True),
    )
    return PageCreateResult.model_validate(result)
