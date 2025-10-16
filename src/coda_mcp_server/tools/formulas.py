"""Formula-related MCP tools for Coda API."""

from typing import Literal

from ..client import CodaClient, clean_params
from ..models import Formula, FormulaList, Method


async def list_formulas(
    client: CodaClient,
    doc_id: str,
    limit: int | None = None,
    page_token: str | None = None,
    sort_by: Literal["name"] | None = None,
) -> FormulaList:
    """List named formulas in a doc.

    Args:
        client: The Coda client instance.
        doc_id: ID of the doc.
        limit: Maximum number of results to return.
        page_token: An opaque token to fetch the next page of results.
        sort_by: How to sort the results.

    Returns:
        List of named formulas with pagination metadata.
    """
    params = {"limit": limit, "pageToken": page_token, "sortBy": sort_by}
    result = await client.request(Method.GET, f"docs/{doc_id}/formulas", params=clean_params(params))
    return FormulaList.model_validate(result)


async def get_formula(client: CodaClient, doc_id: str, formula_id_or_name: str) -> Formula:
    """Get details about a specific formula.

    Args:
        client: The Coda client instance.
        doc_id: ID of the doc.
        formula_id_or_name: ID or name of the formula.

    Returns:
        Formula details including the computed value.
    """
    result = await client.request(Method.GET, f"docs/{doc_id}/formulas/{formula_id_or_name}")
    return Formula.model_validate(result)
