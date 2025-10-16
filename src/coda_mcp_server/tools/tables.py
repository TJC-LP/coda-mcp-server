"""Table and column-related MCP tools for Coda."""

from typing import Literal

from ..client import CodaClient, clean_params
from ..models import Method
from ..models.rows import PushButtonResult
from ..models.tables import Column, ColumnList, Table, TableList


async def list_tables(
    client: CodaClient,
    doc_id: str,
    limit: int | None = None,
    page_token: str | None = None,
    sort_by: Literal["name"] | None = None,
    table_types: list[str] | None = None,
) -> TableList:
    """List tables in a Coda doc.

    Args:
        doc_id: ID of the doc.
        limit: Maximum number of results to return.
        page_token: An opaque token to fetch the next page of results.
        sort_by: How to sort the results (e.g., 'name').
        table_types: Types of tables to include (e.g., ['table', 'view']).

    Returns:
        List of tables with their metadata.
    """
    params = {
        "limit": limit,
        "pageToken": page_token,
        "sortBy": sort_by,
        "tableTypes": table_types,
    }
    result = await client.request(Method.GET, f"docs/{doc_id}/tables", params=clean_params(params))
    return TableList.model_validate(result)


async def get_table(client: CodaClient, doc_id: str, table_id_or_name: str) -> Table:
    """Get details about a specific table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.

    Returns:
        Table details including columns and metadata.
    """
    result = await client.request(Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}")
    return Table.model_validate(result)


async def list_columns(
    client: CodaClient,
    doc_id: str,
    table_id_or_name: str,
    limit: int | None = None,
    page_token: str | None = None,
    visible_only: bool | None = None,
) -> ColumnList:
    """List columns in a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        limit: Maximum number of results to return.
        page_token: An opaque token to fetch the next page of results.
        visible_only: If true, only return visible columns.

    Returns:
        List of columns with their properties.
    """
    params = {
        "limit": limit,
        "pageToken": page_token,
        "visibleOnly": visible_only,
    }
    result = await client.request(
        Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}/columns", params=clean_params(params)
    )
    return ColumnList.model_validate(result)


async def get_column(client: CodaClient, doc_id: str, table_id_or_name: str, column_id_or_name: str) -> Column:
    """Get details about a specific column.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        column_id_or_name: ID or name of the column.

    Returns:
        Column details including format and formula.
    """
    result = await client.request(Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}/columns/{column_id_or_name}")
    return Column.model_validate(result)


async def push_button(
    client: CodaClient,
    doc_id: str,
    table_id_or_name: str,
    row_id_or_name: str,
    column_id_or_name: str,
) -> PushButtonResult:
    """Push a button in a table cell.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_id_or_name: ID or name of the row containing the button.
        column_id_or_name: ID or name of the column containing the button.

    Returns:
        Result of the button push operation.
    """
    result = await client.request(
        Method.POST,
        f"docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}/buttons/{column_id_or_name}",
        json={},
    )
    return PushButtonResult.model_validate(result)
