"""Common types and models shared across Coda MCP server."""

from enum import StrEnum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# HTTP Method Enum
# ============================================================================


class Method(StrEnum):
    """HTTP methods for API requests."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


# ============================================================================
# Common Enums
# ============================================================================


class AccessType(StrEnum):
    """Type of access to a resource."""

    READONLY = "readonly"
    WRITE = "write"
    COMMENT = "comment"
    NONE = "none"


class SortDirection(StrEnum):
    """Direction of a sort for a table or view."""

    ASCENDING = "ascending"
    DESCENDING = "descending"


class SortBy(StrEnum):
    """Determines how the objects returned are sorted."""

    NAME = "name"


class ValueFormat(StrEnum):
    """The format that cell values are returned as."""

    SIMPLE = "simple"
    SIMPLE_WITH_ARRAYS = "simpleWithArrays"
    RICH = "rich"


class TableType(StrEnum):
    """Type of table resource."""

    TABLE = "table"
    VIEW = "view"


# ============================================================================
# Error Response Models
# ============================================================================


class ApiError(BaseModel):
    """An HTTP error resulting from an unsuccessful request."""

    model_config = ConfigDict(populate_by_name=True)

    status_code: int = Field(
        ...,
        alias="statusCode",
        description="HTTP status code of the error.",
    )
    status_message: str = Field(
        ...,
        alias="statusMessage",
        description="HTTP status message of the error.",
    )
    message: str = Field(
        ...,
        description="Any additional context on the error, or the same as statusMessage otherwise.",
    )


class ValidationError(BaseModel):
    """Detail about why a particular field failed request validation."""

    path: str = Field(
        ...,
        description="A path indicating the affected field, in OGNL notation.",
        examples=["parent.child[0]"],
    )
    message: str = Field(
        ...,
        description="An error message.",
        examples=["Expected a string but got a number"],
    )


class CodaDetail(BaseModel):
    """Detail about why this request was rejected."""

    model_config = ConfigDict(populate_by_name=True)

    validation_errors: list[ValidationError] = Field(
        ...,
        alias="validationErrors",
        description="List of validation errors.",
    )


class BadRequestError(ApiError):
    """The request parameters did not conform to expectations."""

    model_config = ConfigDict(populate_by_name=True)

    coda_detail: Optional[CodaDetail] = Field(
        None,
        alias="codaDetail",
        description="Detail about why this request was rejected.",
    )


class UnauthorizedError(ApiError):
    """The API token is invalid or has expired."""

    pass


class ForbiddenError(ApiError):
    """The API token does not grant access to this resource."""

    pass


class NotFoundError(ApiError):
    """The resource could not be located with the current API token."""

    pass


class GoneError(ApiError):
    """The resource has been deleted."""

    pass


class UnprocessableEntityError(ApiError):
    """Unable to process the request."""

    pass


class TooManyRequestsError(ApiError):
    """The client has sent too many requests."""

    pass


# ============================================================================
# Pagination Models
# ============================================================================


class PaginationMetadata(BaseModel):
    """Metadata for paginated responses."""

    model_config = ConfigDict(populate_by_name=True)

    href: Optional[str] = Field(
        None,
        description="API link to these results.",
        examples=["https://coda.io/apis/v1/docs?limit=20"],
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
        examples=["https://coda.io/apis/v1/docs?pageToken=eyJsaW1pd"],
    )


# ============================================================================
# Reference Models
# ============================================================================


class PageReference(BaseModel):
    """Reference to a page."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="ID of the page.", examples=["canvas-IjkLmnO"])
    type: Literal["page"] = Field(..., description="The type of this resource.")
    href: str = Field(
        ...,
        description="API link to the page.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/pages/canvas-IjkLmnO"],
    )
    browser_link: str = Field(
        ...,
        alias="browserLink",
        description="Browser-friendly link to the page.",
        examples=["https://coda.io/d/_dAbCDeFGH/Launch-Status_sumnO"],
    )
    name: str = Field(..., description="Name of the page.", examples=["Launch Status"])


class Icon(BaseModel):
    """Info about the icon."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., description="Name of the icon.")
    type: str = Field(..., description="MIME type of the icon")
    browser_link: str = Field(
        ...,
        alias="browserLink",
        description="Browser-friendly link to an icon.",
        examples=["https://cdn.coda.io/icons/png/color/icon-32.png"],
    )


class Image(BaseModel):
    """Info about the image."""

    model_config = ConfigDict(populate_by_name=True)

    browser_link: str = Field(
        ...,
        alias="browserLink",
        description="Browser-friendly link to an image.",
        examples=["https://codahosted.io/docs/nUYhlXysYO/blobs/bl-lYkYKNzkuT/3f879b9ecfa27448"],
    )
    type: Optional[str] = Field(None, description="MIME type of the image.")
    width: Optional[float] = Field(None, description="The width in pixels of the image.", examples=[800])
    height: Optional[float] = Field(None, description="The height in pixels of the image.", examples=[600])


class FormulaDetail(BaseModel):
    """Detailed information about a formula."""

    model_config = ConfigDict(populate_by_name=True)

    valid: bool = Field(
        ...,
        description="Returns whether or not the given formula is valid.",
        examples=[True],
    )
    is_volatile: Optional[bool] = Field(
        None,
        alias="isVolatile",
        description=(
            "Returns whether or not the given formula can return different results in different contexts "
            "(for example, for different users)."
        ),
        examples=[False],
    )
    has_user_formula: Optional[bool] = Field(
        None,
        alias="hasUserFormula",
        description="Returns whether or not the given formula has a User() formula within it.",
        examples=[False],
    )
    has_today_formula: Optional[bool] = Field(
        None,
        alias="hasTodayFormula",
        description="Returns whether or not the given formula has a Today() formula within it.",
        examples=[False],
    )
    has_now_formula: Optional[bool] = Field(
        None,
        alias="hasNowFormula",
        description="Returns whether or not the given formula has a Now() formula within it.",
        examples=[False],
    )


class PersonValue(BaseModel):
    """A named reference to a person, where the person is identified by email address."""

    model_config = ConfigDict(populate_by_name=True)

    context: str = Field(
        ...,
        alias="@context",
        description='A url describing the schema context for this object, typically "http://schema.org/".',
        examples=["http://schema.org/"],
    )
    type: Literal["Person"] = Field(..., alias="@type", description="The type of this resource.")
    name: str = Field(..., description="The full name of the person.", examples=["Alice Atkins"])
    email: Optional[str] = Field(None, description="The email address of the person.", examples=["alice@atkins.com"])
    additional_type: Optional[str] = Field(
        None,
        alias="additionalType",
        description=(
            "An identifier of additional type info specific to Coda that may not be present in a schema.org taxonomy."
        ),
    )


class DocReference(BaseModel):
    """Reference to a Coda doc.

    A minimal representation of a doc containing just enough information
    to identify and link to it.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(
        ...,
        description="ID of the Coda doc.",
        examples=["AbCDeFGH"],
    )
    type: Literal["doc"] = Field(
        ...,
        description="The type of this resource.",
    )
    href: str = Field(
        ...,
        description="API link to the Coda doc.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH"],
    )
    browser_link: str = Field(
        ...,
        alias="browserLink",
        description="Browser-friendly link to the Coda doc.",
        examples=["https://coda.io/d/_dAbCDeFGH"],
    )


class FolderReference(BaseModel):
    """Reference to a Coda folder.

    Folders are used to organize docs within a workspace.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(
        ...,
        description="ID of the Coda folder.",
        examples=["fl-1Ab234"],
    )
    type: Literal["folder"] = Field(
        ...,
        description="The type of this resource.",
    )
    browser_link: str = Field(
        ...,
        alias="browserLink",
        description="Browser-friendly link to the folder.",
        examples=["https://coda.io/docs?folderId=fl-1Ab234"],
    )
    name: Optional[str] = Field(
        None,
        description="Name of the folder; included if the user has access to the folder.",
        examples=["My docs"],
    )


class WorkspaceReference(BaseModel):
    """Reference to a Coda workspace.

    Workspaces are the top-level organizational unit in Coda, containing
    folders and docs.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(
        ...,
        description="ID of the Coda workspace.",
        examples=["ws-1Ab234"],
    )
    type: Literal["workspace"] = Field(
        ...,
        description="The type of this resource.",
    )
    organization_id: Optional[str] = Field(
        None,
        alias="organizationId",
        description="ID of the organization bound to this workspace, if any.",
        examples=["org-2Bc456"],
    )
    browser_link: str = Field(
        ...,
        alias="browserLink",
        description="Browser-friendly link to the Coda workspace.",
        examples=["https://coda.io/docs?workspaceId=ws-1Ab234"],
    )
    name: Optional[str] = Field(
        None,
        description="Name of the workspace; included if the user has access to the workspace.",
        examples=["My workspace"],
    )


class DocumentMutateResponse(BaseModel):
    """Base response type for an operation that mutates a document.

    This is returned by operations that modify documents and provides
    a request ID for tracking the operation.
    """

    model_config = ConfigDict(populate_by_name=True)

    request_id: str = Field(
        ...,
        alias="requestId",
        description="An arbitrary unique identifier for this request.",
        examples=["abc-123-def-456"],
    )
