from tasks import process_video_task
from schemas import VideoProcessRequest, VideoProcessResponse
import uuid

class VideoService:
    def start_processing(self, payload: VideoProcessRequest) -> VideoProcessResponse:
        task_id = uuid.uuid7()

        process_video_task.apply_async(
            args=[payload.movie_id, str(payload.source_url)],
            task_id=str(task_id)
        )

        return VideoProcessResponse(task_id=task_id, status="accepted")

video_service = VideoService()
