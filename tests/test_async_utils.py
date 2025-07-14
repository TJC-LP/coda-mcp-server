"""Tests for async utility functions."""

import aiohttp
import pytest
from aioresponses import aioresponses

from coda_mcp_server.server import _download_content


class TestDownloadContent:
    """Test the _download_content async utility function."""

    @pytest.mark.asyncio
    async def test_successful_download(self) -> None:
        """Test successful content download."""
        with aioresponses() as mocked:
            test_url = "https://example.com/test"
            test_content = "<html>Test content</html>"
            mocked.get(test_url, body=test_content)

            result = await _download_content(test_url)
            assert result == test_content

    @pytest.mark.asyncio
    async def test_download_empty_content(self) -> None:
        """Test downloading empty content."""
        with aioresponses() as mocked:
            test_url = "https://example.com/empty"
            mocked.get(test_url, body="")

            result = await _download_content(test_url)
            assert result == ""

    @pytest.mark.asyncio
    async def test_download_json_content(self) -> None:
        """Test downloading JSON content."""
        with aioresponses() as mocked:
            test_url = "https://api.example.com/data.json"
            json_content = '{"status": "success", "data": [1, 2, 3]}'
            mocked.get(test_url, body=json_content)

            result = await _download_content(test_url)
            assert result == json_content

    @pytest.mark.asyncio
    async def test_download_with_special_characters(self) -> None:
        """Test downloading content with special characters."""
        with aioresponses() as mocked:
            test_url = "https://example.com/unicode"
            content_with_unicode = "Hello 世界! Special chars: éñ"
            mocked.get(test_url, body=content_with_unicode)

            result = await _download_content(test_url)
            assert result == content_with_unicode

    @pytest.mark.asyncio
    async def test_download_network_error(self) -> None:
        """Test handling of network errors during download."""
        with aioresponses() as mocked:
            test_url = "https://example.com/error"
            mocked.get(test_url, exception=aiohttp.ClientError("Network error"))

            with pytest.raises(aiohttp.ClientError):
                await _download_content(test_url)
