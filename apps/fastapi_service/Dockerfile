FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock* ./

RUN if [ ! -f pyproject.toml ]; then \
    uv init --app && \
    uv add fastapi uvicorn python-multipart boto3 celery redis python-dotenv; \
    fi

RUN if [ -f uv.lock ]; then uv sync --frozen --no-dev; else uv sync; fi

COPY . .

RUN useradd -m -u 1000 fastapi && chown -R fastapi:fastapi /app
USER fastapi

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]