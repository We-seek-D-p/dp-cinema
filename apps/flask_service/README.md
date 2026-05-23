# Flask-сервис

Микросервис для управления пользовательским контентом (UGC). Реализует систему отзывов и рейтингов к фильмам с
обязательной пре-модерацией в Django Admin.

### Архитектура:

Проект реализован по 3-слойной схеме:

- **API Layer (api/v1)**: Эндпоинты, JWT-авторизация и Marshmallow-валидация.
- **Service Layer**: Бизнес-логика, проверка существования фильма в Django через `httpx` и уведомление о модерации.
- **Repository Layer**: Прямое взаимодействие с БД через SQLAlchemy (Soft delete, Unique constraints).

---

### Краткий путь данных:

1. **Создание (POST)**:
    - Пользователь отправляет отзыв на `api/v1/reviews/movies/<id>/submit`.
    - **Auth**: Декоратор `@token_required` в `auth.py` проверяет JWT (общий секрет с Django) и пробрасывает `user_id`.
    - **Service**: `ReviewService` проверяет через `httpx`, существует ли фильм в Django API, и убеждается через
      репозиторий, что этот юзер еще не оставлял отзыв на данный фильм.
    - **DB**: Отзыв сохраняется в PostgreSQL со статусом `pending`.
    - **Moderation**: Сервис вызывает внутренний метод `_notify_moderation`, отправляя `review_id` и контент в Django
      API (`/api/v1/internal/reviews/moderation/`) для отображения в админке.

2. **Модерация (PATCH)**:
    - Модератор в Django Admin одобряет отзыв.
    - **Callback**: Django-сервис отправляет `PATCH` запрос на внутреннюю ручку Flask
      `/api/v1/internal/reviews/<id>/status`.
    - **Security**: Flask проверяет `X-Internal-Token` из заголовков (сверка со значением в `.env`).
    - **Service**: Вызывается `change_review_status`, который переводит отзыв в новый статус.

3. **Отображение (GET)**:
    - При запросе `GET api/v1/reviews/movies/<movie_id>` сервис через `ReviewRepository` возвращает только те записи, у
      которых `status = 'approved'` и `deleted_at IS NULL`.

4. **Обновление и удаление (PUT/DELETE)**:
    - При `PUT` (редактировании) статус отзыва автоматически сбрасывается на `pending`, и он повторно улетает на
      модерацию в Django.
    - При `DELETE` выполняется **Soft Delete** — в БД заполняется поле `deleted_at`, запись перестает быть доступной для
      публичных ручек, но сохраняется в базе.
