"""Tests for CodaClient initialization."""

from pytest import MonkeyPatch

from coda_mcp_server.server import CodaClient


class TestCodaClient:
    """Test the CodaClient class initialization."""

    def test_init_with_explicit_token(self, monkeypatch: MonkeyPatch) -> None:
        """Test client initialization with an explicit API token."""
        # Clear environment variable to ensure we're testing explicit token
        monkeypatch.delenv("CODA_API_KEY", raising=False)

        client = CodaClient(api_token="explicit-token-123")

        assert client.api_token == "explicit-token-123"
        assert client.base_url == "https://coda.io/apis/v1"
        assert client.headers["Authorization"] == "Bearer explicit-token-123"
        assert client.headers["Content-Type"] == "application/json"

    def test_init_with_env_variable(self, monkeypatch: MonkeyPatch) -> None:
        """Test client initialization with environment variable."""
        # Set environment variable
        monkeypatch.setenv("CODA_API_KEY", "env-token-456")

        client = CodaClient()

        assert client.api_token == "env-token-456"
        assert client.headers["Authorization"] == "Bearer env-token-456"

    def test_init_env_variable_takes_precedence(self, monkeypatch: MonkeyPatch) -> None:
        """Test that environment variable takes precedence over explicit token."""
        # Set environment variable
        monkeypatch.setenv("CODA_API_KEY", "env-token-789")

        # Pass explicit token
        client = CodaClient(api_token="explicit-token-000")

        # Environment variable should be used
        assert client.api_token == "env-token-789"
        assert client.headers["Authorization"] == "Bearer env-token-789"

    def test_init_without_token(self, monkeypatch: MonkeyPatch) -> None:
        """Test client initialization without any token."""
        # Clear environment variable
        monkeypatch.delenv("CODA_API_KEY", raising=False)

        client = CodaClient()

        assert client.api_token is None
        assert client.headers["Authorization"] == "Bearer None"  # This would fail in real API calls

    def test_headers_structure(self) -> None:
        """Test that headers are properly structured."""
        client = CodaClient(api_token="test-token")

        assert isinstance(client.headers, dict)
        assert "Authorization" in client.headers
        assert "Content-Type" in client.headers
        assert len(client.headers) == 2

    def test_base_url_format(self) -> None:
        """Test that base URL is correctly formatted."""
        client = CodaClient(api_token="test-token")

        assert client.base_url.startswith("https://")
        assert "coda.io" in client.base_url
        assert client.base_url.endswith("/apis/v1")
        assert not client.base_url.endswith("/")  # No trailing slash
