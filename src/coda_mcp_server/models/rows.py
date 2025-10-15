"""Row and cell value models for Coda MCP server."""

from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .common import DocumentMutateResponse, PersonValue
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
Value = Union[ScalarValue, List[Union[ScalarValue, List[ScalarValue]]]]


# Currency Amount
CurrencyAmount = Union[str, float]


class LinkedDataObject(BaseModel):
    """Base type for a JSON-LD (Linked Data) object."""

    model_config = ConfigDict(populate_by_name=True)

    context: str = Field(
        ...,
        alias="@context",
        description='A url describing the schema context for this object, typically "http://schema.org/".',
        examples=["http://schema.org/"],
    )
    type: LinkedDataType = Field(..., alias="@type", description="A schema.org identifier for the object.")
    additional_type: Optional[str] = Field(
        None,
        alias="additionalType",
        description=(
            "An identifier of additional type info specific to Coda that may not be present in a schema.org taxonomy."
        ),
    )


class UrlValue(LinkedDataObject):
    """A named hyperlink to an arbitrary url."""

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["WebPage"] = Field(..., alias="@type", description="The type of this resource.")
    name: Optional[str] = Field(None, description="The user-visible text of the hyperlink.", examples=["Click me"])
    url: str = Field(..., description="The url of the hyperlink.", examples=["https://coda.io"])


class ImageUrlValue(LinkedDataObject):
    """A named url of an image along with metadata."""

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["ImageObject"] = Field(..., alias="@type", description="The type of this resource.")
    name: Optional[str] = Field(None, description="The name of the image.", examples=["Dogs Playing Poker"])
    url: Optional[str] = Field(
        None,
        description="The url of the image.",
        examples=["https://example.com/dogs-playing-poker.jpg"],
    )
    height: Optional[float] = Field(None, description="The height of the image in pixels.", examples=[480])
    width: Optional[float] = Field(None, description="The width of the image in pixels.", examples=[640])
    status: Optional[ImageStatus] = Field(None, description="The status of the image.")


class CurrencyValue(LinkedDataObject):
    """A monetary value with its associated currency code."""

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["MonetaryAmount"] = Field(..., alias="@type", description="The type of this resource.")
    currency: str = Field(..., description="The 3-letter currency code.", examples=["USD"])
    amount: CurrencyAmount = Field(..., description="The monetary amount as a string or number.", examples=["12.99"])


class RowValue(LinkedDataObject):
    """A value representing a Coda row."""

    model_config = ConfigDict(populate_by_name=True)

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
    table_id: str = Field(..., alias="tableId", description="The ID of the table", examples=["grid-pqRst-U"])
    row_id: str = Field(..., alias="rowId", description="The ID of the row", examples=["i-tuVwxYz"])
    table_url: str = Field(
        ...,
        alias="tableUrl",
        description="The url of the table.",
        examples=["https://coda.io/d/_dAbCDeFGH#Teams-and-Tasks_tpqRst-U"],
    )
    additional_type: Literal["row"] = Field(..., alias="additionalType", description="The type of this resource.")


# Rich Single Value - scalar or structured data
RichSingleValue = Union[ScalarValue, CurrencyValue, ImageUrlValue, PersonValue, UrlValue, RowValue]


# Rich Value - single value or array of values
RichValue = Union[RichSingleValue, List[Union[RichSingleValue, List[RichSingleValue]]]]


# Cell Value - can be simple value or rich value
CellValue = Union[Value, RichValue]


class CellEdit(BaseModel):
    """An edit made to a particular cell in a row."""

    model_config = ConfigDict(populate_by_name=True)

    column: str = Field(
        ...,
        description="Column ID, URL, or name (fragile and discouraged) associated with this edit.",
        examples=["c-tuVwxYz"],
    )
    value: Value = Field(..., description="The value to set in the cell.")


class RowEdit(BaseModel):
    """An edit made to a particular row."""

    model_config = ConfigDict(populate_by_name=True)

    cells: List[CellEdit] = Field(..., description="Array of cell edits for the row.")


class Row(BaseModel):
    """Info about a row."""

    model_config = ConfigDict(populate_by_name=True)

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
        alias="browserLink",
        description="Browser-friendly link to the row.",
        examples=["https://coda.io/d/_dAbCDeFGH#Teams-and-Tasks_tpqRst-U/_rui-tuVwxYz"],
    )
    created_at: datetime = Field(
        ...,
        alias="createdAt",
        description="Timestamp for when the row was created.",
        examples=["2018-04-11T00:18:57.946Z"],
    )
    updated_at: datetime = Field(
        ...,
        alias="updatedAt",
        description="Timestamp for when the row was last modified.",
        examples=["2018-04-11T00:18:57.946Z"],
    )
    values: Dict[str, CellValue] = Field(
        ...,
        description=(
            "Values for a specific row, represented as a hash of column IDs (or names with `useColumnNames`) to values."
        ),
        examples=[{"c-tuVwxYz": "Apple", "c-bCdeFgh": ["$12.34", "$56.78"]}],
    )


class RowDetail(Row):
    """Details about a row."""

    parent: TableReference = Field(..., description="Parent table of the row.")


class RowList(BaseModel):
    """List of rows."""

    model_config = ConfigDict(populate_by_name=True)

    items: List[Row] = Field(..., description="Array of rows.")
    href: Optional[str] = Field(
        None,
        description="API link to these results",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U/rows?limit=20"],
    )
    next_page_token: Optional[str] = Field(
        None,
        alias="nextPageToken",
        description="If specified, an opaque token used to fetch the next page of results.",
        examples=["eyJsaW1pd"],
    )
    next_page_link: Optional[str] = Field(
        None,
        alias="nextPageLink",
        description="If specified, a link that can be used to fetch the next page of results.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U/rows?pageToken=eyJsaW1pd"],
    )
    next_sync_token: Optional[str] = Field(
        None,
        alias="nextSyncToken",
        description=(
            "If specified, an opaque token that can be passed back later to retrieve new results that match "
            "the parameters specified when the sync token was created."
        ),
        examples=["eyJsaW1pd"],
    )


class RowUpdate(BaseModel):
    """Payload for updating a row in a table."""

    model_config = ConfigDict(populate_by_name=True)

    row: RowEdit = Field(..., description="The row data to update.")


class RowUpdateResult(DocumentMutateResponse):
    """The result of a row update."""

    id: str = Field(..., description="ID of the updated row.", examples=["i-tuVwxYz"])


class RowsUpsert(BaseModel):
    """Payload for upserting rows in a table."""

    model_config = ConfigDict(populate_by_name=True)

    rows: List[RowEdit] = Field(..., description="Array of row edits to upsert.")
    key_columns: Optional[List[str]] = Field(
        None,
        alias="keyColumns",
        description=(
            "Optional column IDs, URLs, or names (fragile and discouraged), "
            "specifying columns to be used as upsert keys."
        ),
        examples=[["c-bCdeFgh"]],
    )


class RowsUpsertResult(DocumentMutateResponse):
    """The result of a rows insert/upsert operation."""

    model_config = ConfigDict(populate_by_name=True)

    added_row_ids: Optional[List[str]] = Field(
        None,
        alias="addedRowIds",
        description=("Row IDs for rows that will be added. Only applicable when keyColumns is not set or empty."),
        examples=[["i-bCdeFgh", "i-CdEfgHi"]],
    )


class RowsDelete(BaseModel):
    """Payload for deleting rows from a table."""

    model_config = ConfigDict(populate_by_name=True)

    row_ids: List[str] = Field(
        ...,
        alias="rowIds",
        description="Row IDs to delete.",
        examples=[["i-bCdeFgh", "i-CdEfgHi"]],
    )


class RowsDeleteResult(DocumentMutateResponse):
    """The result of a rows delete operation."""

    model_config = ConfigDict(populate_by_name=True)

    row_ids: List[str] = Field(
        ...,
        alias="rowIds",
        description="Row IDs to delete.",
        examples=[["i-bCdeFgh", "i-CdEfgHi"]],
    )


class RowDeleteResult(DocumentMutateResponse):
    """The result of a row deletion."""

    id: str = Field(..., description="ID of the row to be deleted.", examples=["i-tuVwxYz"])


class PushButtonResult(DocumentMutateResponse):
    """The result of a push button."""

    model_config = ConfigDict(populate_by_name=True)

    row_id: str = Field(
        ..., alias="rowId", description="ID of the row where the button exists.", examples=["i-tuVwxYz"]
    )
    column_id: str = Field(
        ..., alias="columnId", description="ID of the column where the button exists.", examples=["i-tuVwxYz"]
    )


# For convenience, export commonly used types for row creation
# RowCreate is effectively the same as RowEdit in the API
RowCreate = RowEdit
