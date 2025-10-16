"""Row and cell value models for Coda MCP server."""

from datetime import datetime
from typing import Literal, Union

from pydantic import Field

from .common import CodaBaseModel, DocumentMutateResponse, PersonValue
from .tables import TableReference

# Value Format Types
ValueFormat = Literal["simple", "simpleWithArrays", "rich"]


# Rows Sort By
RowsSortBy = Literal["createdAt", "natural", "updatedAt"]


# Image Status
ImageStatus = Literal["live", "deleted", "failed"]


# Linked Data Types
LinkedDataType = Literal["ImageObject", "MonetaryAmount", "Person", "WebPage", "StructuredValue"]


# Scalar Value - primitive types
ScalarValue = Union[str, float, bool]


# Value - scalar or array of scalars
Value = Union[ScalarValue, list[Union[ScalarValue, list[ScalarValue]]]]


# Currency Amount
CurrencyAmount = Union[str, float]


class LinkedDataObject(CodaBaseModel):
    """Base type for a JSON-LD (Linked Data) object."""

    context: str = Field(
        ...,
        alias="@context",
        description='A url describing the schema context for this object, typically "http://schema.org/".',
        examples=["http://schema.org/"],
    )
    type: LinkedDataType = Field(..., alias="@type", description="A schema.org identifier for the object.")
    additional_type: str | None = Field(
        None,
        description=(
            "An identifier of additional type info specific to Coda that may not be present in a schema.org taxonomy."
        ),
    )


class UrlValue(LinkedDataObject):
    """A named hyperlink to an arbitrary url."""

    type: Literal["WebPage"] = Field(..., alias="@type", description="The type of this resource.")
    name: str | None = Field(None, description="The user-visible text of the hyperlink.", examples=["Click me"])
    url: str = Field(..., description="The url of the hyperlink.", examples=["https://coda.io"])


class ImageUrlValue(LinkedDataObject):
    """A named url of an image along with metadata."""

    type: Literal["ImageObject"] = Field(..., alias="@type", description="The type of this resource.")
    name: str | None = Field(None, description="The name of the image.", examples=["Dogs Playing Poker"])
    url: str | None = Field(
        None,
        description="The url of the image.",
        examples=["https://example.com/dogs-playing-poker.jpg"],
    )
    height: float | None = Field(None, description="The height of the image in pixels.", examples=[480])
    width: float | None = Field(None, description="The width of the image in pixels.", examples=[640])
    status: ImageStatus | None = Field(None, description="The status of the image.")


class CurrencyValue(LinkedDataObject):
    """A monetary value with its associated currency code."""

    type: Literal["MonetaryAmount"] = Field(..., alias="@type", description="The type of this resource.")
    currency: str = Field(..., description="The 3-letter currency code.", examples=["USD"])
    amount: CurrencyAmount = Field(..., description="The monetary amount as a string or number.", examples=["12.99"])


class RowValue(LinkedDataObject):
    """A value representing a Coda row."""

    type: Literal["StructuredValue"] = Field(..., alias="@type", description="The type of this resource.")
    name: str = Field(
        ...,
        description="The display name of the row, based on its identifying column.",
        examples=["Apple"],
    )
    url: str = Field(
        ...,
        description="The url of the row.",
        examples=["https://coda.io/d/_dAbCDeFGH#Teams-and-Tasks_tpqRst-U/_rui-tuVwxYz"],
    )
    table_id: str = Field(..., description="The ID of the table", examples=["grid-pqRst-U"])
    row_id: str = Field(..., description="The ID of the row", examples=["i-tuVwxYz"])
    table_url: str = Field(
        ...,
        description="The url of the table.",
        examples=["https://coda.io/d/_dAbCDeFGH#Teams-and-Tasks_tpqRst-U"],
    )
    additional_type: Literal["row"] = Field(..., description="The type of this resource.")


# Rich Single Value - scalar or structured data
RichSingleValue = Union[ScalarValue, CurrencyValue, ImageUrlValue, PersonValue, UrlValue, RowValue]


# Rich Value - single value or array of values
RichValue = Union[RichSingleValue, list[Union[RichSingleValue, list[RichSingleValue]]]]


# Cell Value - can be simple value or rich value
CellValue = Union[Value, RichValue]


class CellEdit(CodaBaseModel):
    """An edit made to a particular cell in a row."""

    column: str = Field(
        ...,
        description="Column ID, URL, or name (fragile and discouraged) associated with this edit.",
        examples=["c-tuVwxYz"],
    )
    value: Value = Field(..., description="The value to set in the cell.")


class RowEdit(CodaBaseModel):
    """An edit made to a particular row."""

    cells: list[CellEdit] = Field(..., description="Array of cell edits for the row.")


class Row(CodaBaseModel):
    """Info about a row."""

    id: str = Field(..., description="ID of the row.", examples=["i-tuVwxYz"])
    type: Literal["row"] = Field(..., description="The type of this resource.")
    href: str = Field(
        ...,
        description="API link to the row.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U/rows/i-RstUv-W"],
    )
    name: str = Field(
        ...,
        description="The display name of the row, based on its identifying column.",
        examples=["Apple"],
    )
    index: int = Field(..., description="Index of the row within the table.", examples=[7])
    browser_link: str = Field(
        ...,
        description="Browser-friendly link to the row.",
        examples=["https://coda.io/d/_dAbCDeFGH#Teams-and-Tasks_tpqRst-U/_rui-tuVwxYz"],
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp for when the row was created.",
        examples=["2018-04-11T00:18:57.946Z"],
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp for when the row was last modified.",
        examples=["2018-04-11T00:18:57.946Z"],
    )
    values: dict[str, CellValue] = Field(
        ...,
        description=(
            "Values for a specific row, represented as a hash of column IDs (or names with `useColumnNames`) to values."
        ),
        examples=[{"c-tuVwxYz": "Apple", "c-bCdeFgh": ["$12.34", "$56.78"]}],
    )


class RowDetail(Row):
    """Details about a row."""

    parent: TableReference = Field(..., description="Parent table of the row.")


class RowList(CodaBaseModel):
    """List of rows."""

    items: list[Row] = Field(..., description="Array of rows.")
    href: str | None = Field(
        None,
        description="API link to these results",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U/rows?limit=20"],
    )
    next_page_token: str | None = Field(
        None,
        description="If specified, an opaque token used to fetch the next page of results.",
        examples=["eyJsaW1pd"],
    )
    next_page_link: str | None = Field(
        None,
        description="If specified, a link that can be used to fetch the next page of results.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U/rows?pageToken=eyJsaW1pd"],
    )
    next_sync_token: str | None = Field(
        None,
        description=(
            "If specified, an opaque token that can be passed back later to retrieve new results that match "
            "the parameters specified when the sync token was created."
        ),
        examples=["eyJsaW1pd"],
    )


class RowUpdate(CodaBaseModel):
    """Payload for updating a row in a table."""

    row: RowEdit = Field(..., description="The row data to update.")


class RowUpdateResult(DocumentMutateResponse):
    """The result of a row update."""

    id: str = Field(..., description="ID of the updated row.", examples=["i-tuVwxYz"])


class RowsUpsert(CodaBaseModel):
    """Payload for upserting rows in a table."""

    rows: list[RowEdit] = Field(..., description="Array of row edits to upsert.")
    key_columns: list[str] | None = Field(
        None,
        description=(
            "Optional column IDs, URLs, or names (fragile and discouraged), "
            "specifying columns to be used as upsert keys."
        ),
        examples=[["c-bCdeFgh"]],
    )


class RowsUpsertResult(DocumentMutateResponse):
    """The result of a rows insert/upsert operation."""

    added_row_ids: list[str] | None = Field(
        None,
        description=("Row IDs for rows that will be added. Only applicable when keyColumns is not set or empty."),
        examples=[["i-bCdeFgh", "i-CdEfgHi"]],
    )


class RowsDelete(CodaBaseModel):
    """Payload for deleting rows from a table."""

    row_ids: list[str] = Field(
        ...,
        description="Row IDs to delete.",
        examples=[["i-bCdeFgh", "i-CdEfgHi"]],
    )


class RowsDeleteResult(DocumentMutateResponse):
    """The result of a rows delete operation."""

    row_ids: list[str] = Field(
        ...,
        description="Row IDs to delete.",
        examples=[["i-bCdeFgh", "i-CdEfgHi"]],
    )


class RowDeleteResult(DocumentMutateResponse):
    """The result of a row deletion."""

    id: str = Field(..., description="ID of the row to be deleted.", examples=["i-tuVwxYz"])


class PushButtonResult(DocumentMutateResponse):
    """The result of a push button."""

    row_id: str = Field(..., description="ID of the row where the button exists.", examples=["i-tuVwxYz"])
    column_id: str = Field(..., description="ID of the column where the button exists.", examples=["i-tuVwxYz"])


# For convenience, export commonly used types for row creation
# RowCreate is effectively the same as RowEdit in the API
RowCreate = RowEdit
