"""Pydantic models for Coda pages."""

from typing import Literal

from pydantic import Field

from .common import CodaBaseModel, DocumentMutateResponse, Icon, Image, PageReference


class Page(CodaBaseModel):
    """Metadata about a page."""

    id: str = Field(..., description="ID of the page.")
    type: Literal["page"] = Field(..., description="The type of this resource.")
    href: str = Field(..., description="API link to the page.")
    browser_link: str = Field(
        ...,
        description="Browser-friendly link to the page.",
        examples=["https://coda.io/d/_dAbCDeFGH/Launch-Status_sumnO"],
    )
    name: str = Field(..., description="Name of the page.", examples=["Launch Status"])
    subtitle: str | None = Field(
        None, description="Subtitle of the page.", examples=["See the status of launch-related tasks."]
    )
    icon: Icon | None = Field(None, description="Icon for the page.")
    image: Image | None = Field(None, description="Cover image for the page.")
    content_type: Literal["canvas", "embed", "syncPage"] = Field(..., description="The type of content on the page.")
    is_hidden: bool = Field(..., description="Whether the page is hidden in the UI.", examples=[True])
    is_effectively_hidden: bool = Field(
        ...,
        description="Whether the page or any of its parents is hidden in the UI.",
        examples=[True],
    )
    parent: PageReference | None = Field(None, description="Reference to the parent page.")
    children: list[PageReference] = Field(..., description="Child pages of this page.")


class PageList(CodaBaseModel):
    """List of pages."""

    items: list[Page] = Field(..., description="List of pages.")
    href: str | None = Field(
        None,
        description="API link to these results.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/pages?limit=20"],
    )
    next_page_token: str | None = Field(
        None, description="Token for fetching the next page of results.", examples=["eyJsaW1pd"]
    )
    next_page_link: str | None = Field(
        None,
        description="Link to the next page of results.",
        examples=["https://coda.io/apis/v1/docs/AbCDeFGH/pages?pageToken=eyJsaW1pd"],
    )


# ============================================================================
# Page Content Models (matches OpenAPI spec exactly)
# ============================================================================


class PageContent(CodaBaseModel):
    """Content for a page (canvas).

    Raw content with format and content string. This is the base content type
    referenced by other content models.
    """

    format: Literal["html", "markdown"] = Field(..., description="Format of the content.")
    content: str = Field(..., description="The actual page content.", examples=["<p><b>This</b> is rich text</p>"])


class CanvasPageContent(CodaBaseModel):
    """Canvas page content with type discriminator.

    Represents a page containing rich text/canvas content.
    Used in PageCreate for specifying initial page content.
    """

    type: Literal["canvas"] = Field(..., description="Indicates a page containing canvas content.")
    canvas_content: PageContent = Field(..., description="The canvas content.")


class EmbedPageContent(CodaBaseModel):
    """Embed page content with type discriminator.

    Represents a page that embeds external content.
    Used in PageCreate for embedding URLs.
    """

    type: Literal["embed"] = Field(..., description="Indicates a page that embeds other content.")
    url: str = Field(..., description="The URL of the content to embed.", examples=["https://example.com"])
    render_method: Literal["compatibility", "standard"] | None = Field(None, description="Render mode for the embed.")


# ============================================================================
# Page Creation & Update Models
# ============================================================================


class PageCreate(CodaBaseModel):
    """Payload for creating a new page in a doc.

    Can be used both for creating standalone pages and as initial_page
    when creating a new doc.
    """

    name: str | None = Field(None, description="Name of the page.", examples=["Launch Status"])
    subtitle: str | None = Field(
        None, description="Subtitle of the page.", examples=["See the status of launch-related tasks."]
    )
    icon_name: str | None = Field(None, description="Name of the icon.", examples=["rocket"])
    image_url: str | None = Field(
        None, description="Url of the cover image to use.", examples=["https://example.com/image.jpg"]
    )
    parent_page_id: str | None = Field(
        None,
        description="The ID of this new page's parent, if creating a subpage.",
        examples=["canvas-tuVwxYz"],
    )
    page_content: CanvasPageContent | EmbedPageContent | None = Field(
        None, description="Content to initialize the page with (canvas or embed)."
    )


class PageContentUpdate(CodaBaseModel):
    """Payload for updating the content of an existing page."""

    insertion_mode: Literal["append", "replace"] = Field(..., description="Mode for inserting content.")
    canvas_content: PageContent = Field(..., description="The canvas content to insert.")


class PageUpdate(CodaBaseModel):
    """Payload for updating a page."""

    name: str | None = Field(None, description="Name of the page.", examples=["Launch Status"])
    subtitle: str | None = Field(
        None, description="Subtitle of the page.", examples=["See the status of launch-related tasks."]
    )
    icon_name: str | None = Field(None, description="Name of the icon.", examples=["rocket"])
    image_url: str | None = Field(
        None, description="Url of the cover image to use.", examples=["https://example.com/image.jpg"]
    )
    is_hidden: bool | None = Field(
        None,
        description=(
            "Whether the page is hidden or not. Note that for pages that cannot be hidden, "
            "like the sole top-level page in a doc, this will be ignored."
        ),
        examples=[True],
    )
    content_update: PageContentUpdate | None = Field(None, description="Content with which to update an existing page.")


# ============================================================================
# Page Operation Results
# ============================================================================


class PageCreateResult(DocumentMutateResponse):
    """The result of a page creation."""

    id: str = Field(..., description="ID of the created page.", examples=["canvas-tuVwxYz"])


class PageUpdateResult(DocumentMutateResponse):
    """The result of a page update."""

    id: str = Field(..., description="ID of the updated page.", examples=["canvas-tuVwxYz"])


class PageDeleteResult(DocumentMutateResponse):
    """The result of a page deletion."""

    id: str = Field(..., description="ID of the page to be deleted.", examples=["canvas-tuVwxYz"])
