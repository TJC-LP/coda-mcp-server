"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def mock_api_key() -> str:
    """Provide a mock API key for tests."""
    return "mock-coda-api-key-67890"
