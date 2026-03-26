# Django Service

Все команды запускаются через пакет `django_service`.

## Подготовка окружения

```shell
uv sync
docker compose up --build
uv run --package django_service python apps/django_service/manage.py migrate
```

## Запуск

```shell
uv run --package django_service python apps/django_service/manage.py runserver
```

Админка: `http://localhost:8000/admin/`. Создать суперпользователя:

```shell
uv run --package django_service python apps/django_service/manage.py createsuperuser
```
