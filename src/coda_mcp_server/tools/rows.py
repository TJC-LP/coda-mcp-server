"""Row-related MCP tools for Coda tables."""

from typing import Any, Literal

from typing_extensions import TypedDict

from ..client import CodaClient, clean_params
from ..models import Method


class CellValue(TypedDict, total=False):
    """Cell value for row operations."""

    column: str  # Column ID or name
    value: Any  # The value to set


class RowUpdate(TypedDict, total=False):
    """Row data for upsert/update operations."""

    cells: list[CellValue]  # Cell values to update


async def list_rows(
    client: CodaClient,
    doc_id: str,
    table_id_or_name: str,
    query: str | None = None,
    sort_by: str | None = None,
    use_column_names: bool | None = None,
    value_format: Literal["simple", "simpleWithArrays", "rich"] | None = None,
    visible_only: bool | None = None,
    limit: int | None = None,
    page_token: str | None = None,
    sync_token: str | None = None,
) -> Any:
    """List rows in a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        query: Query to filter rows (e.g., 'Status="Complete"').
        sort_by: Column to sort by. Use 'natural' for the table's sort order.
        use_column_names: Use column names instead of IDs in the response.
        value_format: Format for cell values (simple, simpleWithArrays, or rich).
        visible_only: If true, only return visible rows.
        limit: Maximum number of results to return.
        page_token: An opaque token to fetch the next page of results.
        sync_token: Token for incremental sync of changes.

    Returns:
        List of rows with their values.
    """
    params = {
        "query": query,
        "sortBy": sort_by,
        "useColumnNames": use_column_names,
        "valueFormat": value_format,
        "visibleOnly": visible_only,
        "limit": limit,
        "pageToken": page_token,
        "syncToken": sync_token,
    }
    return await client.request(
        Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}/rows", params=clean_params(params)
    )


async def get_row(
    client: CodaClient,
    doc_id: str,
    table_id_or_name: str,
    row_id_or_name: str,
    use_column_names: bool | None = None,
    value_format: Literal["simple", "simpleWithArrays", "rich"] | None = None,
) -> Any:
    """Get a specific row from a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_id_or_name: ID or name of the row.
        use_column_names: Use column names instead of IDs in the response.
        value_format: Format for cell values (simple, simpleWithArrays, or rich).

    Returns:
        Row data with values.
    """
    params = {
        "useColumnNames": use_column_names,
        "valueFormat": value_format,
    }
    return await client.request(
        Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}", params=clean_params(params)
    )


async def upsert_rows(
    client: CodaClient,
    doc_id: str,
    table_id_or_name: str,
    rows: list[RowUpdate],
    key_columns: list[str] | None = None,
    disable_parsing: bool | None = None,
) -> Any:
    """Insert or update rows in a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        rows: List of rows to upsert. Each row should have a 'cells' array with column/value pairs.
        key_columns: Column IDs/names to use as keys for matching existing rows.
        disable_parsing: If true, cell values won't be parsed (e.g., URLs won't become links).

    Returns:
        Result of the upsert operation.
    """
    data = {
        "rows": rows,
        "keyColumns": key_columns,
        "disableParsing": disable_parsing,
    }
    return await client.request(Method.POST, f"docs/{doc_id}/tables/{table_id_or_name}/rows", json=clean_params(data))


async def update_row(
    client: CodaClient,
    doc_id: str,
    table_id_or_name: str,
    row_id_or_name: str,
    row: RowUpdate,
    disable_parsing: bool | None = None,
) -> Any:
    """Update a specific row in a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_id_or_name: ID or name of the row to update.
        row: Row data with cells array containing column/value pairs.
        disable_parsing: If true, cell values won't be parsed.

    Returns:
        Updated row data.
    """
    data = {
        "row": row,
        "disableParsing": disable_parsing,
    }
    return await client.request(
        Method.PUT, f"docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}", json=clean_params(data)
    )


async def delete_row(client: CodaClient, doc_id: str, table_id_or_name: str, row_id_or_name: str) -> Any:
    """Delete a specific row from a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_id_or_name: ID or name of the row to delete.

    Returns:
        Result of the deletion.
    """
    return await client.request(Method.DELETE, f"docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}")


async def delete_rows(
    client: CodaClient,
    doc_id: str,
    table_id_or_name: str,
    row_ids: list[str],
) -> Any:
    """Delete multiple rows from a table.

    Args:
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_ids: List of row IDs to delete.

    Returns:
        Result of the deletion operation.
    """
    data = {"rowIds": row_ids}
    return await client.request(Method.DELETE, f"docs/{doc_id}/tables/{table_id_or_name}/rows", json=data)
