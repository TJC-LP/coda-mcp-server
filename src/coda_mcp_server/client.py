"""Coda API client for making authenticated requests."""

import json
import os
from typing import Any

import aiohttp
from pydantic import BaseModel

from .models import Method
from .models.common import CodaBaseModel


def clean_params(params: dict[str, Any]) -> dict[str, Any]:
    """Clean parameters by removing `None` values and converting booleans to strings."""
    cleaned = {}
    for k, v in params.items():
        if v is not None:
            if isinstance(v, bool):
                cleaned[k] = str(v).lower()  # Convert True -> "true", False -> "false"
            else:
                cleaned[k] = v
    return cleaned


class CodaClient:
    """Client for interacting with the Coda API.

    Handles authentication, request formatting, error handling, and response parsing.
    """

    def __init__(self, api_token: str | None = None):
        """Initialize the client.

        Args:
            api_token: Optional API token. If not provided, will check CODA_API_KEY env var.
        """
        self.api_token = os.getenv("CODA_API_KEY", api_token)
        self.base_url = "https://coda.io/apis/v1"
        self.headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}

    async def request(self, method: Method, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make an authenticated request to Coda API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint path (without base URL)
            **kwargs: Additional arguments to pass to aiohttp (params, json, etc.)
                     If json is a CodaBaseModel, it will be auto-serialized.

        Returns:
            Parsed JSON response or empty dict for 204 responses

        Raises:
            Exception: For network errors, API errors, rate limits, or invalid responses
        """
        # Auto-serialize Pydantic models
        if "json" in kwargs and isinstance(kwargs["json"], CodaBaseModel):
            kwargs["json"] = kwargs["json"].model_dump_camel(exclude_none=True)

        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url, headers=self.headers, **kwargs) as response:
                    if response.status == 429:
                        retry_after = response.headers.get("Retry-After", "60")
                        raise Exception(f"Rate limit exceeded. Retry after {retry_after} seconds.")

                    response_text = await response.text()

                    if not response.ok:
                        error_data = None
                        try:
                            error_data = await response.json()
                        except (json.JSONDecodeError, aiohttp.ContentTypeError):
                            # Response body is not valid JSON, which is expected for some error responses
                            error_data = None

                        error_message = f"API Error {response.status}: {response.reason}"
                        if error_data and isinstance(error_data, dict):
                            if "message" in error_data:
                                error_message = f"API Error {response.status}: {error_data['message']}"
                            elif "error" in error_data:
                                error_message = f"API Error {response.status}: {error_data['error']}"
                        elif response_text:
                            error_message = f"API Error {response.status}: {response_text}"

                        raise Exception(error_message)

                    # Return empty dict for 204 No Content responses
                    if response.status == 204:
                        return {}

                    # Try to parse JSON response
                    try:
                        return json.loads(response_text) if response_text else {}
                    except json.JSONDecodeError:
                        raise Exception(f"Invalid JSON response: {response_text[:200]}")

            except aiohttp.ClientError as e:
                raise Exception(f"Network error: {str(e)}")
            except Exception as e:
                # Re-raise our custom exceptions
                if str(e).startswith(("API Error", "Rate limit", "Invalid JSON", "Network error")):
                    raise
                # Wrap unexpected errors
                raise Exception(f"Unexpected error: {str(e)}")
