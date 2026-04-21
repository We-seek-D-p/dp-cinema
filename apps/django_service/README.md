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
