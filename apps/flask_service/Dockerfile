FROM ghcr.io/astral-sh/uv:0.11.14-python3.14-trixie AS build

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /workspace

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.14-slim AS runtime

ENV PATH="/workspace/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd -g 10001 -r appuser \
    && useradd -u 10001 -r -g appuser -s /usr/sbin/nologin appuser

WORKDIR /app
COPY --from=build --chown=appuser:appuser /workspace/.venv /workspace/.venv
COPY --chown=appuser:appuser . /app/

USER appuser

EXPOSE 5001

CMD ["python", "main.py"]
