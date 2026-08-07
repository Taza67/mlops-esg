from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from mlops_esg.api.deps import get_job_service
from mlops_esg.api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ErrorResponse,
    StatusResponse,
)
from mlops_esg.job_service import JobService

router = APIRouter(tags=["jobs"])

_NOT_FOUND = {404: {"model": ErrorResponse, "description": "Unknown job id"}}


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Submit text for zero-shot classification",
    operation_id="submitAnalyzeJob",
)
def submit_analyze(
    payload: AnalyzeRequest,
    jobs: JobService = Depends(get_job_service),
) -> AnalyzeResponse:
    job_id = jobs.submit(payload.text)
    return AnalyzeResponse(id=job_id)


@router.get(
    "/status/{job_id}",
    response_model=StatusResponse,
    summary="Read job status",
    operation_id="getJobStatus",
    responses=_NOT_FOUND,
)
def get_job_status(
    job_id: str,
    jobs: JobService = Depends(get_job_service),
) -> StatusResponse:
    record = jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Unknown job id")
    return StatusResponse(
        id=record.id,
        status=record.status,
        result=record.result,
        error=record.error,
    )
