from fastapi import APIRouter, status

from ...movies.services import video_service
from ...movies.schemas import VideoProcessRequest, VideoProcessResponse

router = APIRouter()

@router.post("/process/", response_model=VideoProcessResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_processing(payload: VideoProcessRequest):
    return video_service.start_processing(payload)
