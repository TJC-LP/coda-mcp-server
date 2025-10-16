"""Common types and models shared across Coda MCP server."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal, Mapping

from pydantic import BaseModel, Field, model_validator
from pydantic.alias_generators import to_camel, to_snake

# ============================================================================
# Base Model
# ============================================================================


def normalize_keys(obj: Any, method: Literal["to_snake", "to_camel"]) -> Any:
    """Normalize keys so they are always snake case."""
    transform = to_snake if method == "to_snake" else to_camel
    if isinstance(obj, Mapping):
        return {transform(k) if isinstance(k, str) else k: normalize_keys(v, method) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_keys(v, method) for v in obj]
    return obj


class CodaBaseModel(BaseModel):
    """Base model for all Coda API models.

    Provides consistent configuration across all models:
    - Accepts camelCase input (from Coda API)
    - Outputs snake_case (Python convention)
    - Uses snake_case JSON schema
    """

    @model_validator(mode="before")
    @classmethod
    def _normalize_input(cls, data: Any) -> Any:
        # Accept both snake_case and camelCase by normalizing everything to snake_case
        return normalize_keys(data, "to_snake")

    def model_dump_camel(
            self,
            *,
            mode: Literal["python", "json"] = "python",
            **kwargs: Any,
    ) -> dict[str, Any]:
        """Returns a dict with camelCase keys.

        All include/exclude/filtering kwargs are applied against snake_case field names (same as .model_dump()).
        Set mode="json" to get JSON-compatible types (datetimes -> ISO strings, etc.).
        """
        data = self.model_dump(mode=mode, **kwargs)  # recursive dump
        return normalize_keys(data, "to_camel")

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


class ApiError(CodaBaseModel):
    """An HTTP error resulting from an unsuccessful request."""

    status_code: int = Field(
        ...,
        description="HTTP status code of the error.",
    )
    status_message: str = Field(
        ...,
        description="HTTP status message of the error.",
    )
    message: str = Field(
        ...,
        description="Any additional context on the error, or the same as statusMessage otherwise.",
    )


class ValidationError(CodaBaseModel):
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


class CodaDetail(CodaBaseModel):
    """Detail about why this request was rejected."""

    validation_errors: list[ValidationError] = Field(
        ...,
        description="List of validation errors.",
    )


class BadRequestError(ApiError):
    """The request parameters did not conform to expectations."""

    coda_detail: CodaDetail | None = Field(
        None,
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


class PaginationMetadata(CodaBaseModel):
    """Metadata for paginated responses."""

    href: str | None = Field(
        None,
        description="API link to these results.",
        examples=["https://coda.io/apis/v1/docs?limit=20"],
    )
    next_page_token: str | None = Field(
        None,
        description="If specified, an opaque token used to fetch the next page of results.",
        examples=["eyJsaW1pd"],
    )
    next_page_link: str | None = Field(
        None,
        description="If specified, a link that can be used to fetch the next page of results.",
        examples=["https://coda.io/apis/v1/docs?pageToken=eyJsaW1pd"],
    )


# ============================================================================
# Reference Models
# ============================================================================


class PageReference(CodaBaseModel):
    """Reference to a page."""

    id: str = Field(..., description="ID of the page.", examples=["canvas-IjkLmnO"])
    type: Literal["page"] = Field(..., description="The type of this resource.")
    href: str = Field(
        ...,
        description="API link to the page.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/pages/canvas-IjkLmnO"],
    )
    browser_link: str = Field(
        ...,
        description="Browser-friendly link to the page.",
        examples=["https://coda.io/d/_dAbCDeFGH/Launch-Status_sumnO"],
    )
    name: str = Field(..., description="Name of the page.", examples=["Launch Status"])


class Icon(CodaBaseModel):
    """Info about the icon."""

    name: str = Field(..., description="Name of the icon.")
    type: str = Field(..., description="MIME type of the icon")
    browser_link: str = Field(
        ...,
        description="Browser-friendly link to an icon.",
        examples=["https://cdn.coda.io/icons/png/color/icon-32.png"],
    )


class Image(CodaBaseModel):
    """Info about the image."""

    browser_link: str = Field(
        ...,
        description="Browser-friendly link to an image.",
        examples=["https://codahosted.io/docs/nUYhlXysYO/blobs/bl-lYkYKNzkuT/3f879b9ecfa27448"],
    )
    type: str | None = Field(None, description="MIME type of the image.")
    width: float | None = Field(None, description="The width in pixels of the image.", examples=[800])
    height: float | None = Field(None, description="The height in pixels of the image.", examples=[600])


class FormulaDetail(CodaBaseModel):
    """Detailed information about a formula."""

    valid: bool = Field(
        ...,
        description="Returns whether or not the given formula is valid.",
        examples=[True],
    )
    is_volatile: bool | None = Field(
        None,
        description=(
            "Returns whether or not the given formula can return different results in different contexts "
            "(for example, for different users)."
        ),
        examples=[False],
    )
    has_user_formula: bool | None = Field(
        None,
        description="Returns whether or not the given formula has a User() formula within it.",
        examples=[False],
    )
    has_today_formula: bool | None = Field(
        None,
        description="Returns whether or not the given formula has a Today() formula within it.",
        examples=[False],
    )
    has_now_formula: bool | None = Field(
        None,
        description="Returns whether or not the given formula has a Now() formula within it.",
        examples=[False],
    )


class PersonValue(CodaBaseModel):
    """A named reference to a person, where the person is identified by email address."""

    context: str = Field(
        ...,
        alias="@context",
        description='A url describing the schema context for this object, typically "http://schema.org/".',
        examples=["http://schema.org/"],
    )
    type: Literal["Person"] = Field(..., alias="@type", description="The type of this resource.")
    name: str = Field(..., description="The full name of the person.", examples=["Alice Atkins"])
    email: str | None = Field(None, description="The email address of the person.", examples=["alice@atkins.com"])
    additional_type: str | None = Field(
        None,
        description=(
            "An identifier of additional type info specific to Coda that may not be present in a schema.org taxonomy."
        ),
    )


class DocReference(CodaBaseModel):
    """Reference to a Coda doc.

    A minimal representation of a doc containing just enough information
    to identify and link to it.
    """

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
        description="Browser-friendly link to the Coda doc.",
        examples=["https://coda.io/d/_dAbCDeFGH"],
    )


class FolderReference(CodaBaseModel):
    """Reference to a Coda folder.

    Folders are used to organize docs within a workspace.
    """

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
        description="Browser-friendly link to the folder.",
        examples=["https://coda.io/docs?folderId=fl-1Ab234"],
    )
    name: str | None = Field(
        None,
        description="Name of the folder; included if the user has access to the folder.",
        examples=["My docs"],
    )


class WorkspaceReference(CodaBaseModel):
    """Reference to a Coda workspace.

    Workspaces are the top-level organizational unit in Coda, containing
    folders and docs.
    """

    id: str = Field(
        ...,
        description="ID of the Coda workspace.",
        examples=["ws-1Ab234"],
    )
    type: Literal["workspace"] = Field(
        ...,
        description="The type of this resource.",
    )
    organization_id: str | None = Field(
        None,
        description="ID of the organization bound to this workspace, if any.",
        examples=["org-2Bc456"],
    )
    browser_link: str = Field(
        ...,
        description="Browser-friendly link to the Coda workspace.",
        examples=["https://coda.io/docs?workspaceId=ws-1Ab234"],
    )
    name: str | None = Field(
        None,
        description="Name of the workspace; included if the user has access to the workspace.",
        examples=["My workspace"],
    )


class User(CodaBaseModel):
    """Information about the current authenticated Coda user."""

    name: str = Field(..., description="Name of the user.", examples=["John Doe"])
    login_id: str = Field(..., description="Email address of the user.", examples=["user@example.com"])
    type: Literal["user"] = Field(..., description="The type of this resource.")
    scoped: bool = Field(..., description="True if the token used is scoped to this user.", examples=[True])
    token_name: str = Field(..., description="Name of the API token if it has one.", examples=["My API Token"])
    href: str = Field(
        ...,
        description="API link to the user.",
        examples=["https://coda.io/apis/v1/whoami"],
    )
    workspace: WorkspaceReference = Field(..., description="The user's default workspace.")


class DocumentMutateResponse(CodaBaseModel):
    """Base response type for an operation that mutates a document.

    This is returned by operations that modify documents and provides
    a request ID for tracking the operation.
    """

    request_id: str = Field(
        ...,
        description="An arbitrary unique identifier for this request.",
        examples=["abc-123-def-456"],
    )
