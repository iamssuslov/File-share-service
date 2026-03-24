from datetime import datetime

from pydantic import BaseModel


class FileResponse(BaseModel):
    id: int
    original_name: str
    content_type: str | None
    size: int
    created_at: datetime

    model_config = {"from_attributes": True}