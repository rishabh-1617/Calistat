import os
import django
from asgiref.sync import sync_to_async

# Initialize Django environment once before importing any models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calisfy_project.settings")
django.setup()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from django.core.management import call_command

from fastapi_app.routers import (
    api_skills,
    api_exercises,
    api_training,
    api_ranking,
    api_community,
    web
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-migrate and auto-seed database on deployment startup if needed
    try:
        await sync_to_async(call_command)("migrate", interactive=False)
        from skills.models import Skill
        has_skills = await sync_to_async(Skill.objects.count)()
        if not has_skills:
            await sync_to_async(call_command)("seed_calisfy")
    except Exception as e:
        print(f"Deployment database check: {e}")
    yield


app = FastAPI(
    title="Calisfy Calisthenics Platform",
    description="High-performance FastAPI asynchronous backend with REST API and Web Interface for Calisfy.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount API Routers
app.include_router(api_skills.router)
app.include_router(api_exercises.router)
app.include_router(api_training.router)
app.include_router(api_ranking.router)
app.include_router(api_community.router)

# Mount Web Page HTML Routers
app.include_router(web.router)


@app.get("/api/health", tags=["System"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "framework": "FastAPI",
        "version": "2.0.0",
        "docs": "/docs"
    }
