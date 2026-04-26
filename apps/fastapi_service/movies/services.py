from schemas import VideoProcessRequest, VideoProcessResponse
import uuid

class VideoService:
    def start_processing(self, payload: VideoProcessRequest) -> VideoProcessResponse:
        task_id = uuid.uuid7()

        return VideoProcessResponse(task_id=task_id, status="processing_started")
