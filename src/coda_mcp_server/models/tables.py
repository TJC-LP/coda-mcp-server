"""Table and column models for Coda MCP server."""

from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from .common import FormulaDetail, PageReference

# Table Type Enum
TableType = Literal["table", "view"]


# Layout Types
Layout = Literal[
    "default",
    "areaChart",
    "barChart",
    "bubbleChart",
    "calendar",
    "card",
    "detail",
    "form",
    "ganttChart",
    "lineChart",
    "masterDetail",
    "pieChart",
    "scatterChart",
    "slide",
    "wordCloud",
]


# Sort Direction
SortDirection = Literal["ascending", "descending"]


# Column Format Types
ColumnFormatType = Literal[
    "text",
    "person",
    "lookup",
    "number",
    "percent",
    "currency",
    "date",
    "dateTime",
    "time",
    "duration",
    "email",
    "link",
    "slider",
    "scale",
    "image",
    "imageReference",
    "attachments",
    "button",
    "checkbox",
    "select",
    "packObject",
    "reaction",
    "canvas",
    "other",
]


# Currency Format Type
CurrencyFormatType = Literal["currency", "accounting", "financial"]


# Email Display Type
EmailDisplayType = Literal["iconAndEmail", "iconOnly", "emailOnly"]


# Link Display Type
LinkDisplayType = Literal["iconOnly", "url", "title", "card", "embed"]


# Image Shape Style
ImageShapeStyle = Literal["auto", "circle"]


# Slider Display Type
SliderDisplayType = Literal["slider", "progress"]


# Checkbox Display Type
CheckboxDisplayType = Literal["toggle", "check"]


# Duration Unit
DurationUnit = Literal["days", "hours", "minutes", "seconds"]


# Icon Set
IconSet = Literal[
    "star",
    "circle",
    "fire",
    "bug",
    "diamond",
    "bell",
    "thumbsup",
    "heart",
    "chili",
    "smiley",
    "lightning",
    "currency",
    "coffee",
    "person",
    "battery",
    "cocktail",
    "cloud",
    "sun",
    "checkmark",
    "lightbulb",
]


class NumberOrNumberFormula(BaseModel):
    """A number or a string representing a formula that evaluates to a number."""

    value: float | str = Field(..., description="A numeric value or formula that evaluates to a numeric value.")


class ColumnReference(BaseModel):
    """Reference to a column."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="ID of the column.", examples=["c-tuVwxYz"])
    type: Literal["column"] = Field(..., description="The type of this resource.")
    href: str = Field(
        ...,
        description="API link to the column.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U/columns/c-tuVwxYz"],
    )


class TableReference(BaseModel):
    """Reference to a table or view."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="ID of the table.", examples=["grid-pqRst-U"])
    type: Literal["table"] = Field(..., description="The type of this resource.")
    table_type: TableType = Field(..., alias="tableType", description="Type of the table.")
    href: str = Field(
        ...,
        description="API link to the table.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U"],
    )
    browser_link: str = Field(
        ...,
        alias="browserLink",
        description="Browser-friendly link to the table.",
        examples=["https://coda.io/d/_dAbCDeFGH/#Teams-and-Tasks_tpqRst-U"],
    )
    name: str = Field(..., description="Name of the table.", examples=["Tasks"])
    parent: PageReference = Field(..., description="Parent page of the table.")


class Sort(BaseModel):
    """A sort applied to a table or view."""

    model_config = ConfigDict(populate_by_name=True)

    column: ColumnReference = Field(..., description="Column to sort by.")
    direction: SortDirection = Field(..., description="Direction of the sort.")


class SimpleColumnFormat(BaseModel):
    """Format of a simple column."""

    model_config = ConfigDict(populate_by_name=True)

    type: ColumnFormatType = Field(..., description="Format type of the column.")
    is_array: bool = Field(..., alias="isArray", description="Whether or not this column is an array.", examples=[True])


class ReferenceColumnFormat(SimpleColumnFormat):
    """Format of a column that refers to another table."""

    table: TableReference = Field(..., description="Reference to the table this column refers to, if applicable.")


class NumericColumnFormat(SimpleColumnFormat):
    """Format of a numeric column."""

    model_config = ConfigDict(populate_by_name=True)

    precision: int | None = Field(None, ge=0, le=10, description="The decimal precision.", examples=[2])
    use_thousands_separator: bool | None = Field(
        None,
        alias="useThousandsSeparator",
        description='Whether to use a thousands separator (like ",") to format the numeric value.',
        examples=[True],
    )


class CurrencyColumnFormat(SimpleColumnFormat):
    """Format of a currency column."""

    model_config = ConfigDict(populate_by_name=True)

    currency_code: str | None = Field(None, alias="currencyCode", description="The currency symbol", examples=["$"])
    precision: int | None = Field(None, ge=0, le=10, description="The decimal precision.", examples=[2])
    format: CurrencyFormatType | None = Field(
        None,
        description="How the numeric value should be formatted (with or without symbol, negative numbers in parens).",
    )


class DateColumnFormat(SimpleColumnFormat):
    """Format of a date column."""

    format: str | None = Field(
        None,
        description="A format string using Moment syntax: https://momentjs.com/docs/#/displaying/",
        examples=["YYYY-MM-DD"],
    )


class TimeColumnFormat(SimpleColumnFormat):
    """Format of a time column."""

    format: str | None = Field(
        None,
        description="A format string using Moment syntax: https://momentjs.com/docs/#/displaying/",
        examples=["h:mm:ss A"],
    )


class DateTimeColumnFormat(SimpleColumnFormat):
    """Format of a date column."""

    model_config = ConfigDict(populate_by_name=True)

    date_format: str | None = Field(
        None,
        alias="dateFormat",
        description="A format string using Moment syntax: https://momentjs.com/docs/#/displaying/",
        examples=["YYYY-MM-DD"],
    )
    time_format: str | None = Field(
        None,
        alias="timeFormat",
        description="A format string using Moment syntax: https://momentjs.com/docs/#/displaying/",
        examples=["h:mm:ss A"],
    )


class DurationColumnFormat(SimpleColumnFormat):
    """Format of a duration column."""

    model_config = ConfigDict(populate_by_name=True)

    precision: int | None = Field(None, description="The precision.", examples=[2])
    max_unit: DurationUnit | None = Field(
        None,
        alias="maxUnit",
        description='The maximum unit of precision, e.g. "hours" if this duration need not include minutes.',
    )


class EmailColumnFormat(SimpleColumnFormat):
    """Format of an email column."""

    display: EmailDisplayType | None = Field(
        None, description="How an email address should be displayed in the user interface."
    )
    autocomplete: bool | None = Field(None, description="Enable autocomplete for email.")


class LinkColumnFormat(SimpleColumnFormat):
    """Format of a link column."""

    display: LinkDisplayType | None = Field(None, description="How a link should be displayed in the user interface.")
    force: bool | None = Field(
        None,
        description="Force embeds to render on the client instead of the server (for sites that require user login).",
        examples=[True],
    )


class ImageReferenceColumnFormat(SimpleColumnFormat):
    """Format of an image reference column."""

    width: NumberOrNumberFormula = Field(..., description="The image width.")
    height: NumberOrNumberFormula = Field(..., description="The image height.")
    style: ImageShapeStyle = Field(..., description="How an image should be displayed.")


class SliderColumnFormat(SimpleColumnFormat):
    """Format of a numeric column that renders as a slider."""

    model_config = ConfigDict(populate_by_name=True)

    minimum: NumberOrNumberFormula | None = Field(None, description="The minimum allowed value for this slider.")
    maximum: NumberOrNumberFormula | None = Field(None, description="The maximum allowed value for this slider.")
    step: NumberOrNumberFormula | None = Field(None, description="The step size (numeric increment) for this slider.")
    display_type: SliderDisplayType | None = Field(
        None, alias="displayType", description="How the slider should be rendered."
    )
    show_value: bool | None = Field(
        None,
        alias="showValue",
        description="Whether the underyling numeric value is also displayed.",
        examples=[True],
    )


class ScaleColumnFormat(SimpleColumnFormat):
    """Format of a numeric column that renders as a scale, like star ratings."""

    maximum: float = Field(..., description="The maximum number allowed for this scale.", examples=[5])
    icon: IconSet = Field(..., description="The icon set to use when rendering the scale, e.g. render a 5 star scale.")


class ButtonColumnFormat(SimpleColumnFormat):
    """Format of a button column."""

    model_config = ConfigDict(populate_by_name=True)

    label: str | None = Field(None, description="Label formula for the button.", examples=["Click me"])
    disable_if: str | None = Field(
        None, alias="disableIf", description="DisableIf formula for the button.", examples=["False()"]
    )
    action: str | None = Field(
        None,
        description="Action formula for the button.",
        examples=['OpenUrl("www.google.com")'],
    )


class CheckboxColumnFormat(SimpleColumnFormat):
    """Format of a checkbox column."""

    model_config = ConfigDict(populate_by_name=True)

    display_type: CheckboxDisplayType = Field(
        ..., alias="displayType", description="How a checkbox should be displayed."
    )


class SelectOption(BaseModel):
    """An option for a select column."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., description="The name of the option.", examples=["Option 1"])
    background_color: str | None = Field(
        None,
        alias="backgroundColor",
        description="The background color of the option.",
        examples=["#ff0000"],
    )
    foreground_color: str | None = Field(
        None,
        alias="foregroundColor",
        description="The foreground color of the option.",
        examples=["#ffffff"],
    )


class SelectColumnFormat(SimpleColumnFormat):
    """Format of a select column."""

    pass


# Column Format Union Type
ColumnFormat = Union[
    ButtonColumnFormat,
    CheckboxColumnFormat,
    DateColumnFormat,
    DateTimeColumnFormat,
    DurationColumnFormat,
    EmailColumnFormat,
    LinkColumnFormat,
    CurrencyColumnFormat,
    ImageReferenceColumnFormat,
    NumericColumnFormat,
    ReferenceColumnFormat,
    SelectColumnFormat,
    SimpleColumnFormat,
    ScaleColumnFormat,
    SliderColumnFormat,
    TimeColumnFormat,
]


class Column(BaseModel):
    """Info about a column."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="ID of the column.", examples=["c-tuVwxYz"])
    type: Literal["column"] = Field(..., description="The type of this resource.")
    href: str = Field(
        ...,
        description="API link to the column.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U/columns/c-tuVwxYz"],
    )
    name: str = Field(..., description="Name of the column.", examples=["Completed"])
    display: bool | None = Field(None, description="Whether the column is the display column.", examples=[True])
    calculated: bool | None = Field(None, description="Whether the column has a formula set on it.", examples=[True])
    formula: str | None = Field(None, description="Formula on the column.", examples=["thisRow.Created()"])
    default_value: str | None = Field(
        None, alias="defaultValue", description="Default value formula for the column.", examples=["Test"]
    )
    format: ColumnFormat = Field(..., description="Format of the column.")


class ColumnDetail(Column):
    """Info about a column with parent table."""

    parent: TableReference = Field(..., description="Parent table of the column.")


class ColumnList(BaseModel):
    """List of columns."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[Column] = Field(..., description="Array of columns.")
    href: str | None = Field(
        None,
        description="API link to these results",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U/columns?limit=20"],
    )
    next_page_token: str | None = Field(
        None,
        alias="nextPageToken",
        description="If specified, an opaque token used to fetch the next page of results.",
        examples=["eyJsaW1pd"],
    )
    next_page_link: str | None = Field(
        None,
        alias="nextPageLink",
        description="If specified, a link that can be used to fetch the next page of results.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U/columns?pageToken=eyJsaW1pd"],
    )


class Table(BaseModel):
    """Metadata about a table."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="ID of the table.", examples=["grid-pqRst-U"])
    type: Literal["table"] = Field(..., description="The type of this resource.")
    table_type: TableType = Field(..., alias="tableType", description="Type of the table.")
    href: str = Field(
        ...,
        description="API link to the table.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U"],
    )
    browser_link: str = Field(
        ...,
        alias="browserLink",
        description="Browser-friendly link to the table.",
        examples=["https://coda.io/d/_dAbCDeFGH/#Teams-and-Tasks_tpqRst-U"],
    )
    name: str = Field(..., description="Name of the table.", examples=["Tasks"])
    parent: PageReference = Field(..., description="Parent page of the table.")
    parent_table: TableReference | None = Field(
        None, alias="parentTable", description="Parent table if this is a view."
    )
    display_column: ColumnReference = Field(..., alias="displayColumn", description="The display column for the table.")
    row_count: int = Field(..., alias="rowCount", description="Total number of rows in the table.", examples=[130])
    sorts: list[Sort] = Field(..., description="Any sorts applied to the table.")
    layout: Layout = Field(..., description="Layout type of the table or view.")
    filter: FormulaDetail | None = Field(
        None, description="Detailed information about the filter formula for the table, if applicable."
    )
    created_at: datetime = Field(
        ...,
        alias="createdAt",
        description="Timestamp for when the table was created.",
        examples=["2018-04-11T00:18:57.946Z"],
    )
    updated_at: datetime = Field(
        ...,
        alias="updatedAt",
        description="Timestamp for when the table was last modified.",
        examples=["2018-04-11T00:18:57.946Z"],
    )
    view_id: str | None = Field(None, alias="viewId", description="ID of the view if this is a view.")


class TableList(BaseModel):
    """List of tables."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[TableReference] = Field(..., description="Array of table references.")
    href: str | None = Field(
        None,
        description="API link to these results",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables?limit=20"],
    )
    next_page_token: str | None = Field(
        None,
        alias="nextPageToken",
        description="If specified, an opaque token used to fetch the next page of results.",
        examples=["eyJsaW1pd"],
    )
    next_page_link: str | None = Field(
        None,
        alias="nextPageLink",
        description="If specified, a link that can be used to fetch the next page of results.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/tables?pageToken=eyJsaW1pd"],
    )
