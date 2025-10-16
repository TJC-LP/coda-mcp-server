"""Doc-related MCP tools for Coda API."""

from typing import Any

from ..client import CodaClient, clean_params
from ..models import (
    Doc,
    DocCreate,
    DocDelete,
    DocList,
    DocumentCreationResult,
    DocUpdate,
    DocUpdateResult,
    Method,
)


async def whoami(client: CodaClient) -> dict[str, Any]:
    """Get information about the current authenticated user.

    Returns:
        User information including name, email, and scoped token info.
    """
    return await client.request(Method.GET, "whoami")


async def get_doc_info(client: CodaClient, doc_id: str) -> Doc:
    """Get info about a particular doc."""
    result = await client.request(Method.GET, f"docs/{doc_id}")
    return Doc.model_validate(result)


async def delete_doc(client: CodaClient, doc_id: str) -> DocDelete:
    """Delete a doc. USE WITH CAUTION."""
    result = await client.request(Method.DELETE, f"docs/{doc_id}")
    return DocDelete.model_validate(result)


async def update_doc(client: CodaClient, doc_id: str, request: DocUpdate) -> DocUpdateResult:
    """Update properties of a doc.

    Args:
        client: The Coda client instance.
        doc_id: ID of the doc to update.
        request: DocUpdate model with update parameters.

    Returns:
        DocUpdateResult with the update result.
    """
    result = await client.request(
        Method.PATCH,
        f"docs/{doc_id}",
        json=request.model_dump(by_alias=True, exclude_none=True),
    )
    return DocUpdateResult.model_validate(result)


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
) -> DocList:
    """List available docs.

    Returns a list of Coda docs accessible by the user, and which they have opened at least once.
    These are returned in the same order as on the docs page: reverse chronological by the latest
    event relevant to the user (last viewed, edited, or shared).

    Args:
        client: The Coda client instance.
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
        DocList containing document list and pagination info.
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
    result = await client.request(Method.GET, "docs", params=clean_params(params))
    return DocList.model_validate(result)


async def create_doc(client: CodaClient, request: DocCreate) -> DocumentCreationResult:
    """Create a new Coda doc.

    Args:
        client: The Coda client instance.
        request: DocCreate model with all doc creation parameters.

    Returns:
        DocumentCreationResult with the created doc's metadata.
    """
    result = await client.request(
        Method.POST,
        "docs",
        json=request.model_dump(by_alias=True, exclude_none=True),
    )
    return DocumentCreationResult.model_validate(result)
