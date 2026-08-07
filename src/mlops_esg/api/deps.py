from fastapi import Request

from mlops_esg.job_service import JobService


def get_job_service(request: Request) -> JobService:
    return request.app.state.job_service
