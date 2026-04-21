# Django Service

Проект открыт в `apps/django_service`, все команды ниже выполняются из этой директории.

## Подготовка окружения

```shell
uv sync
docker compose -f ../../docker-compose.yaml up --build
uv run python manage.py migrate
```

## Запуск

```shell
uv run python manage.py runserver
```

Админка: `http://localhost:8000/admin/`. Создать суперпользователя:

```shell
uv run python manage.py createsuperuser
```
