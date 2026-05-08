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

    headers = {
        "X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN
    }

    try:
        with httpx.Client() as client:
            response = client.post(django_url, json=payload, headers=headers, timeout=10.0)
            response.raise_for_status()
    except Exception as e:
        print(f"Ошибка уведомления Django: {e}")


@celery_app.task(name="movies.tasks.process_video_task")
def process_video_task(movie_id: int, source_url: str):
    base_dir = f"temp_movies/{movie_id}"
    source_dir = os.path.join(base_dir, "source")
    os.makedirs(source_dir, exist_ok=True)


    playlist_name = "playlist.m3u8"
    local_playlist_path = os.path.join(source_dir, playlist_name)
    segment_pattern = os.path.join(source_dir, "seg_%05d.ts")

    ffmpeg_cmd = [
        "ffmpeg", "-i", source_url,
        "-c:v", "libx264", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "128k",
        "-f", "hls", "-hls_time", "6", "-hls_list_size", "0",
        "-hls_segment_filename", segment_pattern,
        local_playlist_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)

        master_playlist_path = os.path.join(base_dir, "master.m3u8")
        with open(master_playlist_path, "w") as f:
            f.write("#EXTM3U\n")
            f.write("#EXT-X-STREAM-INF:BANDWIDTH=10000000,NAME=\"Source\"\n")
            f.write("source/playlist.m3u8\n")

        for root, _, files in os.walk(base_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, base_dir)

                s3_key = f"{movie_id}/{relative_path}"
                s3_client.upload_file(local_path, s3_key)

        final_hls_url = f"{s3_client.endpoint}/{s3_client.bucket_name}/{movie_id}/master.m3u8"
        shutil.rmtree(base_dir)

        notify_django(movie_id, final_hls_url)

        return {"status": "success", "url": final_hls_url}

    except Exception as e:
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
        return {"status": "error", "message": str(e)}
