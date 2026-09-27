from pydantic import BaseModel, ConfigDict, Field


class TaskResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    task_id: str = Field(
        serialization_alias="taskId",
    )
    task: str
