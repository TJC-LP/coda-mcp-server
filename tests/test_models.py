"""Tests for Pydantic models and snake_case serialization."""



from coda_mcp_server.models import (
    Doc,
    DocList,
    Page,
    PageList,
    Row,
    Table,
    User,
)
from coda_mcp_server.models.common import normalize_keys


class TestNormalizeKeys:
    """Test the normalize_keys utility function."""

    def test_to_snake_simple(self) -> None:
        """Test conversion of simple camelCase to snake_case."""
        data = {"firstName": "John", "lastName": "Doe"}
        result = normalize_keys(data, "to_snake")
        assert result == {"first_name": "John", "last_name": "Doe"}

    def test_to_snake_nested(self) -> None:
        """Test conversion of nested objects."""
        data = {
            "userData": {"firstName": "John", "lastName": "Doe"},
            "accountInfo": {"accountId": "123", "accountType": "premium"},
        }
        result = normalize_keys(data, "to_snake")
        assert result == {
            "user_data": {"first_name": "John", "last_name": "Doe"},
            "account_info": {"account_id": "123", "account_type": "premium"},
        }

    def test_to_snake_list(self) -> None:
        """Test conversion of lists of objects."""
        data = {"items": [{"itemName": "Item1"}, {"itemName": "Item2"}]}
        result = normalize_keys(data, "to_snake")
        assert result == {"items": [{"item_name": "Item1"}, {"item_name": "Item2"}]}

    def test_to_camel_simple(self) -> None:
        """Test conversion of simple snake_case to camelCase."""
        data = {"first_name": "John", "last_name": "Doe"}
        result = normalize_keys(data, "to_camel")
        assert result == {"firstName": "John", "lastName": "Doe"}

    def test_to_camel_nested(self) -> None:
        """Test conversion of nested objects to camelCase."""
        data = {
            "user_data": {"first_name": "John", "last_name": "Doe"},
            "account_info": {"account_id": "123", "account_type": "premium"},
        }
        result = normalize_keys(data, "to_camel")
        assert result == {
            "userData": {"firstName": "John", "lastName": "Doe"},
            "accountInfo": {"accountId": "123", "accountType": "premium"},
        }

    def test_preserves_non_string_keys(self) -> None:
        """Test that non-string keys are preserved."""
        data = {1: "one", 2: "two", "normalKey": "value"}
        result = normalize_keys(data, "to_snake")
        assert result == {1: "one", 2: "two", "normal_key": "value"}


class TestCodaBaseModel:
    """Test the CodaBaseModel base class."""

    def test_accepts_camel_case_input(self) -> None:
        """Test that camelCase input is automatically normalized to snake_case."""
        data = {
            "name": "Test User",
            "loginId": "test@example.com",  # camelCase
            "type": "user",
            "scoped": True,
            "tokenName": "test-token",  # camelCase
            "href": "https://coda.io/apis/v1/whoami",
            "workspace": {
                "id": "ws-123",
                "type": "workspace",
                "organizationId": "org-456",  # camelCase
                "browserLink": "https://coda.io/docs",  # camelCase
                "name": "Test Workspace",
            },
        }
        user = User.model_validate(data)
        assert user.login_id == "test@example.com"
        assert user.token_name == "test-token"
        assert user.workspace.organization_id == "org-456"
        assert user.workspace.browser_link == "https://coda.io/docs"

    def test_accepts_snake_case_input(self) -> None:
        """Test that snake_case input also works."""
        data = {
            "name": "Test User",
            "login_id": "test@example.com",  # snake_case
            "type": "user",
            "scoped": True,
            "token_name": "test-token",  # snake_case
            "href": "https://coda.io/apis/v1/whoami",
            "workspace": {
                "id": "ws-123",
                "type": "workspace",
                "organization_id": "org-456",  # snake_case
                "browser_link": "https://coda.io/docs",  # snake_case
                "name": "Test Workspace",
            },
        }
        user = User.model_validate(data)
        assert user.login_id == "test@example.com"
        assert user.token_name == "test-token"

    def test_model_dump_returns_snake_case(self) -> None:
        """Test that model_dump() returns snake_case by default."""
        data = {
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
        user = User.model_validate(data)
        dumped = user.model_dump()

        # Verify top-level fields are snake_case
        assert "login_id" in dumped
        assert "token_name" in dumped
        assert "loginId" not in dumped
        assert "tokenName" not in dumped

        # Verify nested fields are snake_case
        assert "browser_link" in dumped["workspace"]
        assert "browserLink" not in dumped["workspace"]

    def test_model_dump_camel_returns_camel_case(self) -> None:
        """Test that model_dump_camel() returns camelCase for API."""
        data = {
            "name": "Test User",
            "login_id": "test@example.com",
            "type": "user",
            "scoped": True,
            "token_name": "test-token",
            "href": "https://coda.io/apis/v1/whoami",
            "workspace": {
                "id": "ws-123",
                "type": "workspace",
                "organization_id": "org-456",
                "browser_link": "https://coda.io/docs",
                "name": "Test Workspace",
            },
        }
        user = User.model_validate(data)
        dumped = user.model_dump_camel()

        # Verify top-level fields are camelCase
        assert "loginId" in dumped
        assert "tokenName" in dumped
        assert "login_id" not in dumped
        assert "token_name" not in dumped

        # Verify nested fields are camelCase
        assert "browserLink" in dumped["workspace"]
        assert "organizationId" in dumped["workspace"]
        assert "browser_link" not in dumped["workspace"]


class TestDocModels:
    """Test Doc-related models."""

    def test_doc_model_validates(self) -> None:
        """Test that Doc model can be created and validated."""
        data = {
            "id": "test-doc-123",
            "type": "doc",
            "href": "https://coda.io/apis/v1/docs/test-doc-123",
            "browserLink": "https://coda.io/d/_dtest-doc-123",
            "name": "Test Doc",
            "owner": "test@example.com",
            "ownerName": "Test User",
            "createdAt": "2025-01-01T00:00:00.000Z",
            "updatedAt": "2025-01-01T00:00:00.000Z",
            "workspace": {
                "id": "ws-123",
                "type": "workspace",
                "browserLink": "https://coda.io/docs",
                "name": "Test Workspace",
            },
            "folder": {
                "id": "fl-123",
                "type": "folder",
                "browserLink": "https://coda.io/docs?folderId=fl-123",
                "name": "Test Folder",
            },
            "workspaceId": "ws-123",
            "folderId": "fl-123",
        }
        doc = Doc.model_validate(data)
        assert doc.id == "test-doc-123"
        assert doc.owner_name == "Test User"
        assert doc.browser_link == "https://coda.io/d/_dtest-doc-123"
        assert doc.workspace_id == "ws-123"
        assert doc.folder_id == "fl-123"

    def test_doc_list_validates(self) -> None:
        """Test that DocList model can be created."""
        data = {
            "items": [
                {
                    "id": "doc1",
                    "type": "doc",
                    "href": "https://coda.io/apis/v1/docs/doc1",
                    "browserLink": "https://coda.io/d/_ddoc1",
                    "name": "Doc 1",
                    "owner": "test@example.com",
                    "ownerName": "Test User",
                    "createdAt": "2025-01-01T00:00:00.000Z",
                    "updatedAt": "2025-01-01T00:00:00.000Z",
                    "workspace": {
                        "id": "ws-123",
                        "type": "workspace",
                        "browserLink": "https://coda.io/docs",
                        "name": "Test Workspace",
                    },
                    "folder": {
                        "id": "fl-123",
                        "type": "folder",
                        "browserLink": "https://coda.io/docs?folderId=fl-123",
                        "name": "Test Folder",
                    },
                    "workspaceId": "ws-123",
                    "folderId": "fl-123",
                }
            ],
            "href": "https://coda.io/apis/v1/docs",
        }
        doc_list = DocList.model_validate(data)
        assert len(doc_list.items) == 1
        assert doc_list.items[0].owner_name == "Test User"


class TestPageModels:
    """Test Page-related models."""

    def test_page_model_validates(self) -> None:
        """Test that Page model can be created."""
        data = {
            "id": "canvas-test123",
            "type": "page",
            "href": "https://coda.io/apis/v1/docs/doc123/pages/canvas-test123",
            "browserLink": "https://coda.io/d/_ddoc123/_sutest123",
            "name": "Test Page",
            "subtitle": "",
            "contentType": "canvas",
            "isHidden": False,
            "isEffectivelyHidden": False,
            "children": [],
        }
        page = Page.model_validate(data)
        assert page.id == "canvas-test123"
        assert page.content_type == "canvas"
        assert page.is_hidden is False
        assert page.browser_link == "https://coda.io/d/_ddoc123/_sutest123"

    def test_page_list_validates(self) -> None:
        """Test that PageList model can be created."""
        data = {
            "items": [
                {
                    "id": "canvas-test123",
                    "type": "page",
                    "href": "https://coda.io/apis/v1/docs/doc123/pages/canvas-test123",
                    "browserLink": "https://coda.io/d/_ddoc123/_sutest123",
                    "name": "Test Page",
                    "contentType": "canvas",
                    "isHidden": False,
                    "isEffectivelyHidden": False,
                    "children": [],
                }
            ],
            "href": "https://coda.io/apis/v1/docs/doc123/pages",
        }
        page_list = PageList.model_validate(data)
        assert len(page_list.items) == 1


class TestTableModels:
    """Test Table-related models."""

    def test_table_model_validates(self) -> None:
        """Test that Table model can be created."""
        data = {
            "id": "grid-test123",
            "type": "table",
            "tableType": "table",
            "href": "https://coda.io/apis/v1/docs/doc123/tables/grid-test123",
            "browserLink": "https://coda.io/d/_ddoc123#_tugrid-test123",
            "name": "Test Table",
            "parent": {
                "id": "canvas-page123",
                "type": "page",
                "href": "https://coda.io/apis/v1/docs/doc123/pages/canvas-page123",
                "browserLink": "https://coda.io/d/_ddoc123/_supage123",
                "name": "Test Page",
            },
            "rowCount": 10,
            "createdAt": "2025-01-01T00:00:00.000Z",
            "updatedAt": "2025-01-01T00:00:00.000Z",
            "displayColumn": {
                "id": "c-abc123",
                "type": "column",
                "href": "https://coda.io/apis/v1/docs/doc123/tables/grid-test123/columns/c-abc123",
            },
            "sorts": [],
            "layout": "default",
        }
        table = Table.model_validate(data)
        assert table.id == "grid-test123"
        assert table.table_type == "table"
        assert table.row_count == 10


class TestRowModels:
    """Test Row-related models."""

    def test_row_model_validates(self) -> None:
        """Test that Row model can be created."""
        data = {
            "id": "i-test123",
            "type": "row",
            "href": "https://coda.io/apis/v1/docs/doc123/tables/grid-abc/rows/i-test123",
            "name": "Test Row",
            "index": 0,
            "browserLink": "https://coda.io/d/_ddoc123#_tugrid-abc/_rui-test123",
            "createdAt": "2025-01-01T00:00:00.000Z",
            "updatedAt": "2025-01-01T00:00:00.000Z",
            "values": {"col1": "value1", "col2": "value2"},
        }
        row = Row.model_validate(data)
        assert row.id == "i-test123"
        assert row.browser_link == "https://coda.io/d/_ddoc123#_tugrid-abc/_rui-test123"
        assert row.created_at is not None
        assert row.updated_at is not None
