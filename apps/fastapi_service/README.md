# FastAPI-сервис

Микросервис для обработки видео. Принимает внутренний запрос от Django, ставит задачу в Celery,
конвертирует исходный файл в HLS через `ffmpeg`, загружает результат в MinIO/S3 и уведомляет Django о статусе обработки.

### Архитектура:

Проект реализован по схеме API + Service + Worker:

- **API Layer (`api/v1`)**: Внутренний эндпоинт `POST /api/v1/internal/movies/process/`, проверка `X-Internal-Token` и
  валидация входных данных
- **Service Layer (`movies/services.py`)**: Создание `UUID7` task id и постановка задачи `process_video_task` в Celery
- **Queue Layer (`core/celery_app.py`)**: Celery использует Redis как broker и backend
- **Worker Layer (`movies/tasks.py`)**: Основная обработка видео: `ffprobe`, `ffmpeg`, генерация HLS-плейлистов,
  загрузка файлов в MinIO/S3 и callback в Django
- **Repo Layer (`core/s3_client.py`)**: Подключение к MinIO/S3 через `boto3`, проверка bucket и загрузка файлов

### Путь самурая:

1. **Подготовка исходного видео**:
    - Администратор загружает оригинальный видеофайл в MinIO bucket `movies`
    - В Django Admin в поле `source_url` у фильма вставляется публичный URL

2. **Запуск обработки из Django Admin**:
    - Администратор выбирает фильм и запускает action `Запустить обработку видео`
    - Django вызывает `MovieUploadService.process_movie`, переводит фильм в статус `queued` и отправляет запрос в
      FastAPI на `POST /api/v1/internal/movies/process/`
    - В запросе передаются `movie_id` и `source_url`, а в заголовке `X-Internal-Token` передается внутренний токен

3. **Прием запроса в FastAPI**:
    - Ручка `start_processing` проверяет внутренний токен через `validate_internal_token`
    - `VideoService.start_processing` генерирует `UUID7` task id и ставит Celery-задачу `process_video_task`
    - FastAPI сразу возвращает Django ответ `202 Accepted` со статусом `accepted` и `task_id`

4. **Обработка в Celery worker**:
    - Worker отправляет callback в Django со статусом `processing`
    - `ffprobe` читает метаданные исходного файла: ширину, высоту и bitrate
    - По высоте исходника выбираются доступные профили качества: `144p`, `240p`, `360p`, `480p`, `720p`, `1080p`.
    - Для каждого профиля `ffmpeg` создает HLS-плейлист `playlist.m3u8` и `.ts` сегменты
    - Дополнительно создается вариант `source`, где видео копируется без перекодирования, а при необходимости аудио
      переводится в AAC

5. **Загрузка результата в MinIO/S3**:
    - Worker создает `master.m3u8`, который ссылается на все доступные варианты качества
    - Все HLS-файлы загружаются в bucket `movies` по ключам вида `<movie_id>/<relative-path>`
    - Итоговый URL получает формат `http://localhost:9000/movies/<movie_id>/master.m3u8`

6. **Callback в Django**:
    - При успехе worker отправляет callback в Django на `POST /api/v1/internal/movies/processing/callback/` со статусом `completed` и
      итоговым `hls_url`
    - Django сохраняет `hls_url`, переводит фильм в статус `ready` и выставляет `is_published = True`
    - При ошибке worker отправляет статус `failed`, а Django сохраняет текст ошибки в `processing_error`и оставляет
      `is_published = False`
