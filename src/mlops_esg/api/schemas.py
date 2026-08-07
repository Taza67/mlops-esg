from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from mlops_esg.models import JobStatus


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"text": "The firm cut carbon emissions and published a climate report."}
            ]
        }
    )

    text: str = Field(min_length=1, description="Raw text to classify.")


class AnalyzeResponse(BaseModel):
    id: str = Field(description="Job identifier. Poll GET /status/{id}.")


class StatusResponse(BaseModel):
    id: str
    status: JobStatus
    result: str | None = Field(
        default=None,
        description="Winning label when status is done.",
    )
    error: str | None = Field(
        default=None,
        description="Worker error when status is failed.",
    )


class ErrorResponse(BaseModel):
    detail: str
