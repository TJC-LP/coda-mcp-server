"""Pytest configuration and shared fixtures."""

from typing import Any, Callable

import pytest
from aioresponses import aioresponses

from coda_mcp_server.client import CodaClient


@pytest.fixture
def mock_api_key() -> str:
    """Provide a mock API key for tests."""
    return "mock-coda-api-key-67890"


@pytest.fixture
def mock_client(mock_api_key: str) -> CodaClient:
    """Provide a configured CodaClient with test token."""
    return CodaClient(api_token=mock_api_key)


@pytest.fixture
def mock_aioresponses() -> aioresponses:
    """Provide a configured aioresponses instance for mocking HTTP calls."""
    with aioresponses() as m:
        yield m


@pytest.fixture
def mock_coda_doc_response() -> Callable[..., dict[str, Any]]:
    """Factory for Doc API responses (camelCase format from Coda API).

    Returns a function that creates Doc response dictionaries with
    customizable fields. Default values match Coda API camelCase format.
    """
    def _factory(**kwargs: Any) -> dict[str, Any]:
        return {
            "id": kwargs.get("id", "test-doc-123"),
            "type": "doc",
            "href": f"https://coda.io/apis/v1/docs/{kwargs.get('id', 'test-doc-123')}",
            "browserLink": f"https://coda.io/d/_d{kwargs.get('id', 'test-doc-123')}",
            "name": kwargs.get("name", "Test Doc"),
            "owner": kwargs.get("owner", "test@example.com"),
            "ownerName": kwargs.get("owner_name", "Test User"),
            "createdAt": kwargs.get("created_at", "2025-01-01T00:00:00.000Z"),
            "updatedAt": kwargs.get("updated_at", "2025-01-01T00:00:00.000Z"),
            "workspace": kwargs.get("workspace", {
                "id": "ws-123",
                "type": "workspace",
                "browserLink": "https://coda.io/docs",
                "name": "Test Workspace",
            }),
            "folder": kwargs.get("folder", {
                "id": "fl-123",
                "type": "folder",
                "browserLink": "https://coda.io/docs?folderId=fl-123",
                "name": "Test Folder",
            }),
            "workspaceId": "ws-123",
            "folderId": "fl-123",
        }
    return _factory


@pytest.fixture
def mock_coda_page_response() -> Callable[..., dict[str, Any]]:
    """Factory for Page API responses (camelCase format from Coda API)."""
    def _factory(**kwargs: Any) -> dict[str, Any]:
        return {
            "id": kwargs.get("id", "canvas-test123"),
            "type": "page",
            "href": f"https://coda.io/apis/v1/docs/doc123/pages/{kwargs.get('id', 'canvas-test123')}",
            "browserLink": f"https://coda.io/d/_ddoc123/_su{kwargs.get('id', 'test123')}",
            "name": kwargs.get("name", "Test Page"),
            "subtitle": kwargs.get("subtitle", ""),
            "contentType": kwargs.get("content_type", "canvas"),
            "isHidden": kwargs.get("is_hidden", False),
            "isEffectivelyHidden": kwargs.get("is_effectively_hidden", False),
            "children": kwargs.get("children", []),
        }
    return _factory


@pytest.fixture
def mock_coda_row_response() -> Callable[..., dict[str, Any]]:
    """Factory for Row API responses (camelCase format from Coda API)."""
    def _factory(**kwargs: Any) -> dict[str, Any]:
        return {
            "id": kwargs.get("id", "i-test123"),
            "type": "row",
            "href": f"https://coda.io/apis/v1/docs/doc123/tables/grid-abc/rows/{kwargs.get('id', 'i-test123')}",
            "name": kwargs.get("name", "Test Row"),
            "index": kwargs.get("index", 0),
            "browserLink": f"https://coda.io/d/_ddoc123#_tugrid-abc/_ru{kwargs.get('id', 'i-test123')}",
            "createdAt": kwargs.get("created_at", "2025-01-01T00:00:00.000Z"),
            "updatedAt": kwargs.get("updated_at", "2025-01-01T00:00:00.000Z"),
            "values": kwargs.get("values", {"col1": "value1", "col2": "value2"}),
        }
    return _factory


@pytest.fixture
def mock_coda_user_response() -> dict[str, Any]:
    """Provide a standard User API response (camelCase format)."""
    return {
        "name": "Test User",
        "loginId": "test@example.com",
        "type": "user",
        "scoped": True,
        "tokenName": "test-token",
        "href": "https://coda.io/apis/v1/whoami",
        "workspace": {
            "id": "ws-123",
            "type": "workspace",
            "browserLink": "https://coda.io/docs",
            "name": "Test Workspace",
        },
    }
