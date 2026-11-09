FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY app ./app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv sync --locked --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]