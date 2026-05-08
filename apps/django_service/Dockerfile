FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock* ./

RUN if [ ! -f pyproject.toml ]; then \
    uv init --app && \
    uv add django djangorestframework django-cors-headers psycopg2-binary python-dotenv boto3 django-storages; \
    fi

RUN if [ -f uv.lock ]; then uv sync --frozen --no-dev; else uv sync; fi

COPY . .

RUN useradd -m -u 1000 django && chown -R django:django /app
USER django

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]