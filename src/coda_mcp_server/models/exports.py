"""Pydantic models for Coda page content export API.

This module contains models for the asynchronous page content export workflow:
1. Begin export with BeginPageContentExportRequest -> BeginPageContentExportResponse
2. Poll status with PageContentExportStatusResponse
3. Download content from downloadLink when status is "complete"

The export API is asynchronous because rendering page content can take time.
Poll the href URL from the initial response to check status and get the download link.
"""

from typing import Literal

from pydantic import Field

from .common import CodaBaseModel


class BeginPageContentExportRequest(CodaBaseModel):
    """Request for beginning an export of page content.

    The export process is asynchronous - this request initiates the export
    and returns a status URL to poll for completion.
    """

    output_format: Literal["html", "markdown"] = Field(
        ...,
        description="Supported output content formats that can be requested for getting content for an existing page.",
    )


class BeginPageContentExportResponse(CodaBaseModel):
    """Response when beginning an export of page content.

    Contains the export request ID and a status URL to poll for completion.
    The export happens asynchronously - poll the href URL to check status
    and get the download link when complete.
    """

    id: str = Field(
        ...,
        description="The identifier of this export request.",
        examples=["AbCDeFGH"],
    )
    status: str = Field(
        ...,
        description="The status of this export.",
        examples=["complete"],
    )
    href: str = Field(
        ...,
        description=(
            "The URL that reports the status of this export. Poll this URL to get "
            "the content URL when the export has completed."
        ),
        examples=["https://coda.io/apis/v1/docs/somedoc/pages/somepage/export/some-request-id"],
    )


class PageContentExportStatusResponse(CodaBaseModel):
    """Response when requesting the status of a page content export.

    Poll this endpoint to check export status. When status is "complete",
    the downloadLink field will contain the URL to download the exported content.
    The download link typically expires after a short time - call this endpoint
    again to get a fresh link if needed.

    Status values:
    - "inProgress": Export is still being processed
    - "complete": Export finished successfully, downloadLink is available
    - "failed": Export failed, error field contains details
    """

    id: str = Field(
        ...,
        description="The identifier of this export request.",
        examples=["AbCDeFGH"],
    )
    status: Literal["inProgress", "failed", "complete"] = Field(
        ...,
        description="The status of this export.",
        examples=["complete"],
    )
    href: str = Field(
        ...,
        description="The URL that reports the status of this export.",
        examples=["https://coda.io/apis/v1/docs/somedoc/pages/somepage/export/some-request-id"],
    )
    download_link: str | None = Field(
        None,
        description=(
            "Once the export completes, the location where the resulting export "
            "file can be downloaded; this link typically expires after a short "
            "time. Call this method again to get a fresh link."
        ),
        examples=["https://coda.io/blobs/DOC_EXPORT_RENDERING/some-request-id"],
    )
    error: str | None = Field(
        None,
        description="Message describing an error, if this export failed.",
    )
    content: str | None = Field(
        None,
        description=(
            "The actual exported page content (HTML or markdown). "
            "This is automatically downloaded when status is 'complete'. "
            "Note: This field is a convenience enhancement not in the OpenAPI spec."
        ),
    )
