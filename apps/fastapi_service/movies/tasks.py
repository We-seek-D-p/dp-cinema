import os
import shutil
import httpx
import subprocess
from core.celery_app import celery_app
from core.s3_client import s3_client
from core.config import settings


def notify_django(movie_id: int, hls_url: str):
    django_url = f"{settings.DJANGO_API_URL}/api/v1/movies/callback/"

    payload = {
        "movie_id": movie_id,
        "hls_url": hls_url,
        "status": "completed"
    }

    try:
        with httpx.Client() as client:
            response = client.post(django_url, json=payload, timeout=10.0)
            response.raise_for_status()
    except Exception as e:
        print(f"Ошибка уведомления Django: {e}")


@celery_app.task(name="movies.tasks.process_video_task", bind=True)
def process_video_task(movie_id: int, source_url: str):
    base_dir = f"temp_movies/{movie_id}"
    os.makedirs(base_dir, exist_ok=True)
    playlist_name = "playlist.m3u8"
    local_playlist_path = os.path.join(base_dir, playlist_name)

    ffmpeg_cmd = [
        "ffmpeg", "-i", source_url,
        "-c:v", "libx264", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "128k",
        "-f", "hls", "-hls_time", "6", "-hls_list_size", "0",
        "-hls_segment_filename", f"{base_dir}/seg_%03d.ts",
        local_playlist_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        for file_name in os.listdir(base_dir):
            local_file_path = os.path.join(base_dir, file_name)
            s3_key = f"{movie_id}/{file_name}"
            s3_client.upload_file(local_file_path, s3_key)

        final_hls_url = f"{s3_client.endpoint}/{s3_client.bucket_name}/{movie_id}/{playlist_name}"

        shutil.rmtree(base_dir)

        notify_django(movie_id, final_hls_url)

        return {"status": "success", "url": final_hls_url}

    except Exception as e:
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
        return {"status": "error", "message": str(e)}
