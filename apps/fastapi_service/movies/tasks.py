from core.celery_app import celery_app

@celery_app.task(name="process_video_task", bind=True)
def process_video_task(self, movie_id: int, source_url: str):
    return {"status": "success", "id": movie_id}

