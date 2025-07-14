"""Tests for utility functions."""

from typing import Any

import pytest

from coda_mcp_server.server import clean_params


class TestCleanParams:
    """Test the clean_params utility function."""

    def test_removes_none_values(self) -> None:
        """Test that None values are removed from the params."""
        params = {"key1": "value1", "key2": None, "key3": "value3"}
        result = clean_params(params)
        assert result == {"key1": "value1", "key3": "value3"}
        assert "key2" not in result

    def test_converts_booleans_to_strings(self) -> None:
        """Test that boolean values are converted to lowercase strings."""
        params = {"enabled": True, "disabled": False, "name": "test"}
        result = clean_params(params)
        assert result == {"enabled": "true", "disabled": "false", "name": "test"}

    def test_handles_empty_dict(self) -> None:
        """Test that empty dictionary returns empty dictionary."""
        params: dict[str, Any] = {}
        result = clean_params(params)
        assert result == {}

    def test_preserves_other_types(self) -> None:
        """Test that other types are preserved as-is."""
        params = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }
        result = clean_params(params)
        assert result == params

    @pytest.mark.parametrize(
        "input_params,expected",
        [
            ({"a": None, "b": None}, {}),
            ({"a": True, "b": False, "c": None}, {"a": "true", "b": "false"}),
            ({"key": ""}, {"key": ""}),  # Empty string is not None
            ({"key": 0}, {"key": 0}),  # Zero is not None
            ({"key": False}, {"key": "false"}),  # False is not None
        ],
    )
    def test_various_edge_cases(self, input_params: dict[str, Any], expected: dict[str, Any]) -> None:
        """Test various edge cases with parametrized inputs."""
        result = clean_params(input_params)
        assert result == expected

    def test_does_not_modify_original(self) -> None:
        """Test that the original dictionary is not modified."""
        params = {"key1": "value1", "key2": None, "bool": True}
        original = params.copy()
        result = clean_params(params)

        # Original should remain unchanged
        assert params == original
        # Result should be different
        assert result != params
