import os
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import chat

app = FastAPI(
    title="AWS Container Service",
    description="A containerized FastAPI application with AWS ECS management capabilities.",
    version="2.0.0",
)

app.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
)


def get_ecs_metadata():
    """Retrieve ECS task metadata when running inside ECS."""
    metadata_uri = os.getenv("ECS_CONTAINER_METADATA_URI_V4")

    if not metadata_uri:
        return None

    try:
        with urllib.request.urlopen(
            f"{metadata_uri}/task", timeout=2
        ) as response:
            return json.loads(response.read())
    except Exception:
        return None


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "aws-container-service",
        "version": app.version,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/info")
async def info():
    metadata = get_ecs_metadata()

    return {
        "service": "aws-container-service",
        "version": app.version,
        "runtime": "Docker",
        "orchestration": "Amazon ECS",
        "compute": "AWS Fargate",
        "region": os.getenv("AWS_REGION", "ap-southeast-2"),
        "environment": "production" if metadata else "unknown",
        "task": {
            "task_arn": metadata.get("TaskARN"),
            "family": metadata.get("Family"),
            "revision": metadata.get("Revision"),
            "availability_zone": metadata.get("AvailabilityZone")
        } if metadata else None
    }


@app.get("/api/status")
async def service_status():
    metadata = get_ecs_metadata()

    return {
        "status": "operational",
        "service": "aws-container-service",
        "version": app.version,
        "platform": "AWS ECS Fargate",
        "task_running": metadata is not None,
        "checked_at": datetime.now(timezone.utc).isoformat()
    }

# Serve the React frontend when its production build is available.
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if frontend_dist.exists():
    app.mount(
        "/",
        StaticFiles(directory=frontend_dist, html=True),
        name="frontend",
    )
else:
    @app.get("/")
    async def root():
        return {
            "name": "AWS Container Service",
            "description": "A containerized FastAPI application running on AWS ECS.",
            "version": app.version,
            "status": "running",
            "endpoints": {
                "health": "/health",
                "info": "/info",
                "documentation": "/docs",
                "openapi": "/openapi.json",
                "chat": "/chat/"
            }
        }
