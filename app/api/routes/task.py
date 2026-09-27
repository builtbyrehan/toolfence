from fastapi import APIRouter, HTTPException

from app.api.schemas.task import TaskResponse
from app.api.services.dashboard import read_task_context


router = APIRouter()


@router.get(
    "/task",
    response_model=TaskResponse,
)
def get_task() -> TaskResponse:
    try:
        task = read_task_context()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return TaskResponse(
        task_id=task["task_id"],
        task=task["task"],
    )
