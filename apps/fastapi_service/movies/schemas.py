from pydantic import BaseModel, HttpUrl, Field, UUID7
import uuid


class VideoProcessRequest(BaseModel):
    movie_id: int = Field(..., gt=0, description="ID фильма")
    source_url: HttpUrl


class VideoProcessResponse(BaseModel):
    task_id: UUID7
    status: str = "accepted"


class VideoNotifyRequest(BaseModel):
    movie_id: int
    hls_url: HttpUrl
    status: str = "completed"
