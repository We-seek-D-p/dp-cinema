import json
import os
import shutil
import subprocess

import httpx
from core.celery_app import celery_app
from core.config import settings
from core.s3_client import s3_client

from .transcode_models import QUALITY_PROFILES, HlsVariant


def get_video_meta(source_url: str):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0", "-show_entries",
        "stream=width,height:format=bit_rate", "-of", "json", source_url
    ]

    result = subprocess.run(  # noqa: S603
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)

    streams = data.get("streams") or []
    if not streams:
        raise ValueError(f"No video stream found: {source_url}")

    stream = streams[0]
    format_info = data.get("format") or {}

    if "width" not in stream or "height" not in stream:
        raise ValueError(f"Video stream has no dimensions: {source_url}")

    width = int(stream["width"])
    height = int(stream["height"])

    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid video dimensions {width}x{height} for {source_url}")

    bit_rate_raw = stream.get("bit_rate") or format_info.get("bit_rate")
    bit_rate = int(bit_rate_raw) if bit_rate_raw else 10_000_000

    if bit_rate <= 0:
        raise ValueError(f"Invalid video bitrate {bit_rate} for {source_url}")

    return width, height, bit_rate


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
            response = client.post(
                django_url,
                json=payload,
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
    except Exception as e:
        print(f"Ошибка уведомления Django: {e}")


def _run_cmd(cmd: list[str]):
    result = subprocess.run(  # noqa: S603
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or result.stdout.strip() or "ffmpeg failed"
        )


@celery_app.task(name="movies.tasks.process_video_task")
def process_video_task(movie_id: int, source_url: str):
    base_dir = f"temp_movies/{movie_id}"
    os.makedirs(base_dir, exist_ok=True)

    try:
        source_width, source_height, source_bitrate = get_video_meta(source_url)

        variants: list[HlsVariant] = []
        available_profiles = [p for p in QUALITY_PROFILES if source_height >= p.height]

        for profile in available_profiles:
            profile_dir = profile.dir
            variant_dir = os.path.join(base_dir, profile_dir)
            os.makedirs(variant_dir, exist_ok=True)

            local_playlist_path = os.path.join(variant_dir, "playlist.m3u8")
            segment_pattern = os.path.join(variant_dir, "seg_%05d.ts")

            ffmpeg_cmd = [
                "ffmpeg", "-i", source_url,
                "-vf", f"scale=-2:{profile.height}",
                "-c:v", "libx264", "-preset", "veryfast",
                "-b:v", profile.video_bitrate,
                "-maxrate", profile.max_rate,
                "-bufsize", profile.buf_size,
                "-c:a", "aac", "-b:a", "128k",
                "-f", "hls", "-hls_time", "6", "-hls_list_size", "0",
                "-hls_segment_filename", segment_pattern,
                local_playlist_path
            ]
            _run_cmd(ffmpeg_cmd)

            rendered_height = profile.height
            rendered_width = int(source_width * rendered_height / source_height)
            if rendered_width % 2 != 0:
                rendered_width += 1

            variants.append(
                HlsVariant(
                    name=profile.name,
                    dir=profile_dir,
                    bandwidth=profile.bandwidth,
                    width=rendered_width,
                    height=rendered_height,
                )
            )

        source_dir = os.path.join(base_dir, "source")
        os.makedirs(source_dir, exist_ok=True)
        source_playlist_path = os.path.join(source_dir, "playlist.m3u8")
        source_segment_pattern = os.path.join(source_dir, "seg_%05d.ts")

        source_cmd_copy = [
            "ffmpeg", "-i", source_url,
            "-c:v", "copy", "-c:a", "copy",
            "-f", "hls", "-hls_time", "6", "-hls_list_size", "0",
            "-hls_segment_filename", source_segment_pattern,
            source_playlist_path
        ]

        try:
            _run_cmd(source_cmd_copy)
        except RuntimeError:
            source_cmd_aac = [
                "ffmpeg", "-i", source_url,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-f", "hls", "-hls_time", "6", "-hls_list_size", "0",
                "-hls_segment_filename", source_segment_pattern,
                source_playlist_path
            ]
            _run_cmd(source_cmd_aac)

        variants.append(
            HlsVariant(
                name="Source",
                dir="source",
                bandwidth=source_bitrate,
                width=source_width,
                height=source_height,
            )
        )

        master_playlist_path = os.path.join(base_dir, "master.m3u8")
        with open(master_playlist_path, "w") as f:
            f.write("#EXTM3U\n")
            for variant in variants:
                f.write(
                    f"#EXT-X-STREAM-INF:BANDWIDTH={variant.bandwidth},"
                    f"RESOLUTION={variant.width}x{variant.height},"
                    f"NAME=\"{variant.name}\"\n"
                )
                f.write(f"{variant.dir}/playlist.m3u8\n")

        for root, _, files in os.walk(base_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, base_dir)

                s3_key = f"{movie_id}/{relative_path}"
                s3_client.upload_file(local_path, s3_key)

        final_hls_url = (
            f"{s3_client.endpoint}/{s3_client.bucket_name}/{movie_id}/master.m3u8"
        )
        shutil.rmtree(base_dir)

        notify_django(movie_id, final_hls_url)

        return {"status": "success", "url": final_hls_url}

    except Exception as e:
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
        return {"status": "error", "message": str(e)}
