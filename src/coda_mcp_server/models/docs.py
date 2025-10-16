"""Pydantic models for Coda doc-related API resources.

This module contains models for working with Coda docs, including:
- Doc: Full metadata about a doc
- DocList: List of docs with pagination
- DocCreate: Payload for creating a new doc
- DocUpdate: Payload for updating a doc
- DocDelete: Result of doc deletion
- DocPublish: Payload for publishing a doc
- DocPublished: Published doc information
- DocSize: Information about doc size/components
- PublishResult, UnpublishResult: Results of publish operations
- DocumentCreationResult: Result of doc creation
- DocUpdateResult: Result of doc update
"""

from typing import Literal

from pydantic import Field

from .common import (
    CodaBaseModel,
    DocReference,
    DocumentMutateResponse,
    FolderReference,
    Icon,
    WorkspaceReference,
)


class DocSize(CodaBaseModel):
    """The number of components within a Coda doc.

    Provides information about the size and complexity of a doc.
    """

    total_row_count: float = Field(
        ...,
        description="The number of rows contained within all tables of the doc.",
        examples=[31337],
    )
    table_and_view_count: float = Field(
        ...,
        description="The total number of tables and views contained within the doc.",
        examples=[42],
    )
    page_count: float = Field(
        ...,
        description="The total number of page contained within the doc.",
        examples=[10],
    )
    over_api_size_limit: bool = Field(
        ...,
        description="If true, indicates that the doc is over the API size limit.",
        examples=[False],
    )


class DocCategory(CodaBaseModel):
    """The category applied to a doc.

    Categories are used to classify published docs in the Coda gallery.
    """

    name: str = Field(
        ...,
        description="Name of the category.",
        examples=["Project Management"],
    )


class DocPublishMode(str):
    """Which interaction mode the published doc should use.

    - view: Users can only view the doc
    - play: Users can interact with controls but not edit
    - edit: Users can fully edit the doc
    """

    VIEW = "view"
    PLAY = "play"
    EDIT = "edit"


class DocPublished(CodaBaseModel):
    """Information about the publishing state of the document.

    Contains details about how a doc is published and shared publicly.
    """

    description: str | None = Field(
        None,
        description="Description of the published doc.",
        examples=["Hello World!"],
    )
    browser_link: str = Field(
        ...,
        description="URL to the published doc.",
        examples=["https://coda.io/@coda/hello-world"],
    )
    image_link: str | None = Field(
        None,
        description="URL to the cover image for the published doc.",
    )
    discoverable: bool = Field(
        ...,
        description="If true, indicates that the doc is discoverable.",
        examples=[True],
    )
    earn_credit: bool = Field(
        ...,
        description=(
            "If true, new users may be required to sign in to view content within this document. "
            "You will receive Coda credit for each user who signs up via your doc."
        ),
        examples=[True],
    )
    mode: Literal["view", "play", "edit"] = Field(
        ...,
        description="Which interaction mode the published doc should use.",
    )
    categories: list[DocCategory] = Field(
        ...,
        description="Categories applied to the doc.",
        examples=[["Project Management"]],
    )


class Doc(CodaBaseModel):
    """Metadata about a Coda doc.

    Contains comprehensive information about a doc including ownership,
    timestamps, location in workspace/folder hierarchy, and publishing state.
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
    icon: Icon | None = Field(
        None,
        description="Info about the icon.",
    )
    name: str = Field(
        ...,
        description="Name of the doc.",
        examples=["Product Launch Hub"],
    )
    owner: str = Field(
        ...,
        description="Email address of the doc owner.",
        examples=["user@example.com"],
    )
    owner_name: str = Field(
        ...,
        description="Name of the doc owner.",
        examples=["Some User"],
    )
    doc_size: DocSize | None = Field(
        None,
        description="The number of components within a Coda doc.",
    )
    source_doc: DocReference | None = Field(
        None,
        description="Reference to a Coda doc from which this doc was copied, if any.",
    )
    created_at: str = Field(
        ...,
        description="Timestamp for when the doc was created.",
        examples=["2018-04-11T00:18:57.946Z"],
    )
    updated_at: str = Field(
        ...,
        description="Timestamp for when the doc was last modified.",
        examples=["2018-04-11T00:18:57.946Z"],
    )
    published: DocPublished | None = Field(
        None,
        description="Information about the publishing state of the document.",
    )
    folder: FolderReference = Field(
        ...,
        description="Reference to the folder containing this doc.",
    )
    workspace: WorkspaceReference = Field(
        ...,
        description="Reference to the workspace containing this doc.",
    )
    workspace_id: str = Field(
        ...,
        description="ID of the Coda workspace containing this doc.",
        examples=["ws-1Ab234"],
        deprecated=True,
    )
    folder_id: str = Field(
        ...,
        description="ID of the Coda folder containing this doc.",
        examples=["fl-1Ab234"],
        deprecated=True,
    )


class DocList(CodaBaseModel):
    """List of Coda docs.

    Contains a paginated list of docs with optional pagination tokens
    to fetch additional results.
    """

    items: list[Doc] = Field(
        ...,
        description="Array of Coda docs.",
    )
    href: str | None = Field(
        None,
        description="API link to these results",
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


class PageContentFormat(str):
    """Supported content types for page (canvas) content.

    - html: HTML content
    - markdown: Markdown content
    """

    HTML = "html"
    MARKDOWN = "markdown"


class PageContent(CodaBaseModel):
    """Content for a page (canvas).

    The actual content can be provided in HTML or Markdown format.
    """

    format: Literal["html", "markdown"] = Field(
        ...,
        description="Format of the page content.",
    )
    content: str = Field(
        ...,
        description="The actual page content.",
        examples=["<p><b>This</b> is rich text</p>"],
    )


class PageEmbedRenderMethod(str):
    """Render mode for a page using the Embed page type.

    - compatibility: Legacy rendering mode
    - standard: Standard rendering mode
    """

    COMPATIBILITY = "compatibility"
    STANDARD = "standard"


class CanvasPageContent(CodaBaseModel):
    """Canvas page content with type discriminator.

    Represents a page containing rich text/canvas content.
    """

    type: Literal["canvas"] = Field(
        ...,
        description="Indicates a page containing canvas content.",
    )
    canvas_content: PageContent = Field(
        ...,
        description="Content for the canvas page.",
    )


class EmbedPageContent(CodaBaseModel):
    """Embed page content with type discriminator.

    Represents a page that embeds external content.
    """

    type: Literal["embed"] = Field(
        ...,
        description="Indicates a page that embeds other content.",
    )
    url: str = Field(
        ...,
        description="The URL of the content to embed.",
        examples=["https://example.com"],
    )
    render_method: Literal["compatibility", "standard"] | None = Field(
        None,
        description="Render mode for the embed.",
    )


class PageCreate(CodaBaseModel):
    """Payload for creating a new page in a doc.

    Used when creating a doc with an initial page, or when adding
    a page to an existing doc.
    """

    name: str | None = Field(
        None,
        description="Name of the page.",
        examples=["Launch Status"],
    )
    subtitle: str | None = Field(
        None,
        description="Subtitle of the page.",
        examples=["See the status of launch-related tasks."],
    )
    icon_name: str | None = Field(
        None,
        description="Name of the icon.",
        examples=["rocket"],
    )
    image_url: str | None = Field(
        None,
        description="Url of the cover image to use.",
        examples=["https://example.com/image.jpg"],
    )
    parent_page_id: str | None = Field(
        None,
        description="The ID of this new page's parent, if creating a subpage.",
        examples=["canvas-tuVwxYz"],
    )
    page_content: CanvasPageContent | None = Field(
        None,
        description="Content that can be added to a page at creation time.",
    )


class DocCreate(CodaBaseModel):
    """Payload for creating a new doc.

    A new doc can be created from scratch or by copying an existing doc.
    You can optionally specify a folder/workspace location and initial page content.
    """

    title: str | None = Field(
        None,
        description="Title of the new doc. Defaults to 'Untitled'.",
        examples=["Project Tracker"],
    )
    source_doc: str | None = Field(
        None,
        description="An optional doc ID from which to create a copy.",
        examples=["iJKlm_noPq"],
    )
    timezone: str | None = Field(
        None,
        description="The timezone to use for the newly created doc.",
        examples=["America/Los_Angeles"],
    )
    folder_id: str | None = Field(
        None,
        description=(
            'The ID of the folder within which to create this doc. Defaults to your "My docs" folder in the '
            "oldest workspace you joined; this is subject to change. You can get this ID by opening the folder "
            "in the docs list on your computer and grabbing the `folderId` query parameter."
        ),
        examples=["fl-ABcdEFgHJi"],
    )
    initial_page: PageCreate | None = Field(
        None,
        description="The contents of the initial page of the doc.",
    )


class DocUpdate(CodaBaseModel):
    """Payload for updating a doc.

    Allows updating basic doc properties like title and icon.
    """

    title: str | None = Field(
        None,
        description="Title of the doc.",
        examples=["Project Tracker"],
    )
    icon_name: str | None = Field(
        None,
        description="Name of the icon.",
        examples=["rocket"],
    )


class DocDelete(CodaBaseModel):
    """The result of a doc deletion.

    Returned when a doc is successfully deleted.
    """

    pass


class DocPublish(CodaBaseModel):
    """Payload for publishing a doc or updating its publishing information.

    Controls how the doc appears when published and who can access it.
    """

    slug: str | None = Field(
        None,
        description="Slug for the published doc.",
        examples=["my-doc"],
    )
    discoverable: bool | None = Field(
        None,
        description="If true, indicates that the doc is discoverable.",
        examples=[True],
    )
    earn_credit: bool | None = Field(
        None,
        description=(
            "If true, new users may be required to sign in to view content within this document. "
            "You will receive Coda credit for each user who signs up via your doc."
        ),
        examples=[True],
    )
    category_names: list[str] | None = Field(
        None,
        description="The names of categories to apply to the document.",
        examples=[["Project management"]],
    )
    mode: Literal["view", "play", "edit"] | None = Field(
        None,
        description="Which interaction mode the published doc should use.",
    )


class PublishResult(DocumentMutateResponse):
    """The result of publishing a doc.

    Extends DocumentMutateResponse with any publish-specific fields.
    """

    pass


class UnpublishResult(CodaBaseModel):
    """The result of unpublishing a doc.

    Returned when a doc is successfully unpublished.
    """

    pass


class DocumentCreationResult(CodaBaseModel):
    """The result of a doc creation.

    Similar to Doc but includes a requestId for tracking the creation operation.
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
    icon: Icon | None = Field(
        None,
        description="Info about the icon.",
    )
    name: str = Field(
        ...,
        description="Name of the doc.",
        examples=["Product Launch Hub"],
    )
    owner: str = Field(
        ...,
        description="Email address of the doc owner.",
        examples=["user@example.com"],
    )
    owner_name: str = Field(
        ...,
        description="Name of the doc owner.",
        examples=["Some User"],
    )
    doc_size: DocSize | None = Field(
        None,
        description="The number of components within a Coda doc.",
    )
    source_doc: DocReference | None = Field(
        None,
        description="Reference to a Coda doc from which this doc was copied, if any.",
    )
    created_at: str = Field(
        ...,
        description="Timestamp for when the doc was created.",
        examples=["2018-04-11T00:18:57.946Z"],
    )
    updated_at: str = Field(
        ...,
        description="Timestamp for when the doc was last modified.",
        examples=["2018-04-11T00:18:57.946Z"],
    )
    published: DocPublished | None = Field(
        None,
        description="Information about the publishing state of the document.",
    )
    folder: FolderReference = Field(
        ...,
        description="Reference to the folder containing this doc.",
    )
    workspace: WorkspaceReference = Field(
        ...,
        description="Reference to the workspace containing this doc.",
    )
    workspace_id: str = Field(
        ...,
        description="ID of the Coda workspace containing this doc.",
        examples=["ws-1Ab234"],
        deprecated=True,
    )
    folder_id: str = Field(
        ...,
        description="ID of the Coda folder containing this doc.",
        examples=["fl-1Ab234"],
        deprecated=True,
    )
    request_id: str = Field(
        ...,
        description="An arbitrary unique identifier for this request.",
        examples=["abc-123-def-456"],
    )


class DocUpdateResult(CodaBaseModel):
    """The result of a doc update.

    Returned when a doc is successfully updated.
    """

    pass


class DocCategoryList(CodaBaseModel):
    """A list of categories that can be applied to a doc.

    Used to discover available categories for publishing docs.
    """

    items: list[DocCategory] = Field(
        ...,
        description="Categories for the doc.",
    )
