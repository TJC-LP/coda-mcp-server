"""Pydantic models for Coda formula operations."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .common import PageReference
from .rows import ScalarValue


class FormulaReference(BaseModel):
    """Reference to a formula.

    A minimal representation of a formula containing just enough information
    to identify and link to it.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="ID of the formula.", examples=["f-fgHijkLm"])
    type: Literal["formula"] = Field(..., description="The type of this resource.")
    href: str = Field(
        ...,
        description="API link to the formula.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/formulas/f-fgHijkLm"],
    )
    name: str = Field(..., description="Name of the formula.", examples=["Sum of expenses"])
    parent: PageReference = Field(..., description="Parent page of the formula.")


class Formula(FormulaReference):
    """Details about a formula.

    Extends FormulaReference with the computed value of the formula.
    """

    value: ScalarValue = Field(..., description="The computed value of the formula.")


class FormulaList(BaseModel):
    """List of formulas in a doc.

    Paginated response containing formula references.
    """

    model_config = ConfigDict(populate_by_name=True)

    items: list[FormulaReference] = Field(..., description="List of named formulas in the doc.")
    href: str | None = Field(
        None,
        description="API link to these results",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/formulas?limit=20"],
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
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/formulas?pageToken=eyJsaW1pd"],
    )
