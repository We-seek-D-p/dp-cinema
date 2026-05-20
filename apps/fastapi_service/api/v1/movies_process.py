from hmac import compare_digest

from core.config import settings
from fastapi import APIRouter, Depends, Header, HTTPException, status
from movies.schemas import VideoProcessRequest, VideoProcessResponse
from movies.services import video_service

router = APIRouter()


def validate_internal_token(
    x_internal_token: str | None = Header(default=None),
) -> None:
    if not x_internal_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Internal-Token",
        )
    if not compare_digest(x_internal_token, settings.INTERNAL_SERVICE_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid X-Internal-Token",
        )


@router.post(
    "/process/",
    response_model=VideoProcessResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_processing(
    payload: VideoProcessRequest,
    _: None = Depends(validate_internal_token),
):
    return video_service.start_processing(payload)
