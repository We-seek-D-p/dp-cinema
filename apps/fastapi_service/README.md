# FastAPI-сервис

### Краткий путь данных:

1. Этот сервис принимает запрос от Django-сервиса от ручки process_video, которая вызывает сервис MovieUploadService,
   где внутри вызывается внутренний метод _send_to_fastapi для отправки запроса о загрузке фильма FastAPI.
2. Ручка FastAPI, start_processing, принимает запрос от Django-сервиса и вызывает VideoService, а именно - метод
   start_processing, что создаёт таску process_video_task и кидает её в Celery. Задача process_video_task - с помощью
   ffmpeg сегментировать видео во временную директорию, и по окончании, скопировать сегменты и нужные файлы в s3, после
   чего временная директорию очищается.
3. Далее всё там же, в process_video_task, вызывается notify_django - Django-сервис получает оповещение в
   `api/v1/movies/callback` с итоговым `hls_url`.
4. Ручка в Django-сервисе вызывается MovieUploadService, а именно метод finalize_processing, где вызывается метод
   репозитория finalize_processing, сохраняя в бд `hls_url` и `is_published = True`.
