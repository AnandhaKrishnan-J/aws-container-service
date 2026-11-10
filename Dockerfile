# Frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Backend Service
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv sync --locked --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

COPY app ./app

# Copy production React build into the application
COPY --from=frontend-builder /frontend/dist ./frontend/dist

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]