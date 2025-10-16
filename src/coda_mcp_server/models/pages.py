"""Pydantic models for Coda pages."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .common import DocumentMutateResponse, Icon, Image, PageReference


class Page(BaseModel):
    """Metadata about a page."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="ID of the page.")
    type: Literal["page"] = Field(..., description="The type of this resource.")
    href: str = Field(..., description="API link to the page.")
    browser_link: str = Field(
        ...,
        alias="browserLink",
        description="Browser-friendly link to the page.",
        examples=["https://coda.io/d/_dAbCDeFGH/Launch-Status_sumnO"],
    )
    name: str = Field(..., description="Name of the page.", examples=["Launch Status"])
    subtitle: str | None = Field(
        None, description="Subtitle of the page.", examples=["See the status of launch-related tasks."]
    )
    icon: Icon | None = Field(None, description="Icon for the page.")
    image: Image | None = Field(None, description="Cover image for the page.")
    content_type: Literal["canvas", "embed", "syncPage"] = Field(
        ..., alias="contentType", description="The type of content on the page."
    )
    is_hidden: bool = Field(..., alias="isHidden", description="Whether the page is hidden in the UI.", examples=[True])
    is_effectively_hidden: bool = Field(
        ...,
        alias="isEffectivelyHidden",
        description="Whether the page or any of its parents is hidden in the UI.",
        examples=[True],
    )
    parent: PageReference | None = Field(None, description="Reference to the parent page.")
    children: list[PageReference] = Field(..., description="Child pages of this page.")


class PageList(BaseModel):
    """List of pages."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[Page] = Field(..., description="List of pages.")
    href: str | None = Field(
        None,
        description="API link to these results.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/pages?limit=20"],
    )
    next_page_token: str | None = Field(
        None, alias="nextPageToken", description="Token for fetching the next page of results.", examples=["eyJsaW1pd"]
    )
    next_page_link: str | None = Field(
        None,
        alias="nextPageLink",
        description="Link to the next page of results.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/pages?pageToken=eyJsaW1pd"],
    )


class CanvasContent(BaseModel):
    """Content for a page canvas with format and content text."""

    format: Literal["html", "markdown"] = Field(..., description="Format of the content.")
    content: str = Field(..., description="The actual page content.", examples=["<p><b>This</b> is rich text</p>"])


class PageContent(BaseModel):
    """Page content wrapper for canvas type."""

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["canvas"] = Field(..., description="Indicates a page containing canvas content.")
    canvas_content: CanvasContent = Field(..., alias="canvasContent", description="The canvas content.")


class PageCreate(BaseModel):
    """Payload for creating a new page in a doc."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(None, description="Name of the page.", examples=["Launch Status"])
    subtitle: str | None = Field(
        None, description="Subtitle of the page.", examples=["See the status of launch-related tasks."]
    )
    icon_name: str | None = Field(None, alias="iconName", description="Name of the icon.", examples=["rocket"])
    image_url: str | None = Field(
        None, alias="imageUrl", description="Url of the cover image to use.", examples=["https://example.com/image.jpg"]
    )
    parent_page_id: str | None = Field(
        None,
        alias="parentPageId",
        description="The ID of this new page's parent, if creating a subpage.",
        examples=["canvas-tuVwxYz"],
    )
    page_content: PageContent | None = Field(
        None, alias="pageContent", description="Content to initialize the page with."
    )


class InitialPage(BaseModel):
    """Initial page configuration for doc creation."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(None, description="Name of the page.")
    subtitle: str | None = Field(None, description="Subtitle of the page.")
    icon_name: str | None = Field(None, alias="iconName", description="Name of the icon.")
    image_url: str | None = Field(None, alias="imageUrl", description="URL of the cover image.")
    parent_page_id: str | None = Field(None, alias="parentPageId", description="The ID of this new page's parent.")
    page_content: PageContent | None = Field(
        None, alias="pageContent", description="Content to initialize the page with."
    )


class PageContentUpdate(BaseModel):
    """Payload for updating the content of an existing page."""

    model_config = ConfigDict(populate_by_name=True)

    insertion_mode: Literal["append", "replace"] = Field(
        ..., alias="insertionMode", description="Mode for inserting content."
    )
    canvas_content: CanvasContent = Field(..., alias="canvasContent", description="The canvas content to insert.")


class PageUpdate(BaseModel):
    """Payload for updating a page."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(None, description="Name of the page.", examples=["Launch Status"])
    subtitle: str | None = Field(
        None, description="Subtitle of the page.", examples=["See the status of launch-related tasks."]
    )
    icon_name: str | None = Field(None, alias="iconName", description="Name of the icon.", examples=["rocket"])
    image_url: str | None = Field(
        None, alias="imageUrl", description="Url of the cover image to use.", examples=["https://example.com/image.jpg"]
    )
    is_hidden: bool | None = Field(
        None,
        alias="isHidden",
        description=(
            "Whether the page is hidden or not. Note that for pages that cannot be hidden, "
            "like the sole top-level page in a doc, this will be ignored."
        ),
        examples=[True],
    )
    content_update: PageContentUpdate | None = Field(
        None, alias="contentUpdate", description="Content with which to update an existing page."
    )


class PageCreateResult(DocumentMutateResponse):
    """The result of a page creation."""

    id: str = Field(..., description="ID of the created page.", examples=["canvas-tuVwxYz"])


class PageUpdateResult(DocumentMutateResponse):
    """The result of a page update."""

    id: str = Field(..., description="ID of the updated page.", examples=["canvas-tuVwxYz"])


class PageDeleteResult(DocumentMutateResponse):
    """The result of a page deletion."""

    id: str = Field(..., description="ID of the page to be deleted.", examples=["canvas-tuVwxYz"])
