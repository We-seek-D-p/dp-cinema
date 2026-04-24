# Django Service

Проект открыт в `apps/django_service`, все команды ниже выполняются из этой директории.

## Подготовка окружения

```shell
uv sync
docker compose -f ../../docker-compose.yaml up --build
uv run python manage.py migrate
```

Альтернатива через `justfile`:

```shell
just install
just migrate
```

## Запуск

```shell
uv run python manage.py runserver
```

Через `just`:

```shell
just run
```

Админка: `http://localhost:8000/admin/`. Создать суперпользователя:

```shell
uv run python manage.py createsuperuser
```

## Запуск тестов

```shell
uv run python manage.py test
```

Через `just`:

```shell
just test
```

## API v1

- `POST /api/v1/users/register/` - регистрация пользователя.
- `POST /api/v1/users/login/` - вход и получение JWT-токенов.
- `GET /api/v1/users/profile/{id}/` - получение публичного профиля пользователя.
- `PATCH /api/v1/users/profile/{id}/` - обновление профиля пользователя.
- `DELETE /api/v1/users/profile/{id}/` - деактивация аккаунта пользователя.
- `POST /api/v1/users/restore/` - восстановление аккаунта по email.
- `GET /api/v1/movies/` - список опубликованных фильмов (с фильтрацией, поиском и сортировкой).
- `GET /api/v1/movies/{id}/` - детальная информация по фильму.
- `GET /api/v1/movies/genres/` - список жанров.
- `GET /api/v1/movies/genres/{id}/` - детальная информация по жанру.
- `GET /api/v1/watchlist/` - список watchlist текущего пользователя.
- `POST /api/v1/watchlist/` - добавление фильма в watchlist.
- `DELETE /api/v1/watchlist/{movie_id}/` - удаление фильма из watchlist.
