"""Row-related MCP tools for Coda tables."""

from typing import Literal

from ..client import CodaClient, clean_params
from ..models import (
    Method,
    Row,
    RowDeleteResult,
    RowEdit,
    RowList,
    RowsDelete,
    RowsDeleteResult,
    RowsUpsert,
    RowsUpsertResult,
    RowUpdate,
    RowUpdateResult,
)


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
) -> RowList:
    """List rows in a table.

    Args:
        client: The Coda client instance.
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
        RowList with rows and pagination metadata.
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
    result = await client.request(
        Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}/rows", params=clean_params(params)
    )
    return RowList.model_validate(result)


async def get_row(
    client: CodaClient,
    doc_id: str,
    table_id_or_name: str,
    row_id_or_name: str,
    use_column_names: bool | None = None,
    value_format: Literal["simple", "simpleWithArrays", "rich"] | None = None,
) -> Row:
    """Get a specific row from a table.

    Args:
        client: The Coda client instance.
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
    result = await client.request(
        Method.GET, f"docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}", params=clean_params(params)
    )
    return Row.model_validate(result)


async def upsert_rows(
    client: CodaClient,
    doc_id: str,
    table_id_or_name: str,
    rows: list[RowEdit],
    key_columns: list[str] | None = None,
    disable_parsing: bool | None = None,
) -> RowsUpsertResult:
    """Insert or update rows in a table.

    Args:
        client: The Coda client instance.
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        rows: List of rows to upsert. Each row should have a 'cells' array with column/value pairs.
        key_columns: Column IDs/names to use as keys for matching existing rows.
        disable_parsing: If true, cell values won't be parsed (e.g., URLs won't become links).

    Returns:
        RowsUpsertResult with the result of the upsert operation.
    """
    # Build the request model
    request = RowsUpsert(rows=rows, key_columns=key_columns)

    # Add disableParsing as a query parameter if provided
    params = {"disableParsing": disable_parsing} if disable_parsing is not None else None

    result = await client.request(
        Method.POST,
        f"docs/{doc_id}/tables/{table_id_or_name}/rows",
        json=request,
        params=clean_params(params) if params else None,
    )
    return RowsUpsertResult.model_validate(result)


async def update_row(
    client: CodaClient,
    doc_id: str,
    table_id_or_name: str,
    row_id_or_name: str,
    row: RowEdit,
    disable_parsing: bool | None = None,
) -> RowUpdateResult:
    """Update a specific row in a table.

    Args:
        client: The Coda client instance.
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_id_or_name: ID or name of the row to update.
        row: Row data with cells array containing column/value pairs.
        disable_parsing: If true, cell values won't be parsed.

    Returns:
        RowUpdateResult with the updated row data.
    """
    # Build the request model
    request = RowUpdate(row=row)

    # Add disableParsing as a query parameter if provided
    params = {"disableParsing": disable_parsing} if disable_parsing is not None else None

    result = await client.request(
        Method.PUT,
        f"docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}",
        json=request,
        params=clean_params(params) if params else None,
    )
    return RowUpdateResult.model_validate(result)


async def delete_row(client: CodaClient, doc_id: str, table_id_or_name: str, row_id_or_name: str) -> RowDeleteResult:
    """Delete a specific row from a table.

    Args:
        client: The Coda client instance.
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_id_or_name: ID or name of the row to delete.

    Returns:
        RowDeleteResult with the result of the deletion.
    """
    result = await client.request(Method.DELETE, f"docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}")
    return RowDeleteResult.model_validate(result)


async def delete_rows(
    client: CodaClient,
    doc_id: str,
    table_id_or_name: str,
    row_ids: list[str],
) -> RowsDeleteResult:
    """Delete multiple rows from a table.

    Args:
        client: The Coda client instance.
        doc_id: ID of the doc.
        table_id_or_name: ID or name of the table.
        row_ids: List of row IDs to delete.

    Returns:
        RowsDeleteResult with the result of the deletion operation.
    """
    # Build the request model
    request = RowsDelete(row_ids=row_ids)

    result = await client.request(
        Method.DELETE,
        f"docs/{doc_id}/tables/{table_id_or_name}/rows",
        json=request,
    )
    return RowsDeleteResult.model_validate(result)
