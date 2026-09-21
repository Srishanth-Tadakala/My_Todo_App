"""
FastAPI Main Application
Configures middleware, exception handlers, routers, and APScheduler lifecycle.
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import logger
from app.core.responses import error_response, success_response
from app.routers import (
    analytics, assignments, attachments, auth, calendar, certifications, dashboard,
    events, exams, hackathons, internships, lists, notifications, projects, reminders,
    search, subjects, tags, timetable, todos, users
)
from app.scheduler.scheduler import get_scheduler, start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and graceful shutdown."""
    settings = get_settings()
    logger.info(f"Starting Advanced Todo API ({settings.APP_ENV})...")
    # Start APScheduler in single-instance mode
    try:
        start_scheduler()
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

    yield

    logger.info("Shutting down Advanced Todo API...")
    try:
        stop_scheduler()
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")


settings = get_settings()

app = FastAPI(
    title="Advanced Todo Application API",
    description="Production-grade backend for Advanced Todo, Academic Timetable, Career Tracking, and Smart Reminders.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 2. Structured Request Logging Middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    # Avoid noisy health check logs in stdout
    if request.url.path not in ("/health", "/health/ready"):
        logger.info(
            f"{request.method} {request.url.path} - Status: {response.status_code} - {duration_ms}ms"
        )
    return response


# 3. Global Exception Handlers (Standard Error Envelope)
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(
        code="VALIDATION_ERROR",
        message="Invalid request payload or query parameters.",
        status_code=422,
        details=exc.errors(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(
        code="HTTP_ERROR",
        message=str(exc.detail),
        status_code=exc.status_code,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server error: {exc}")
    return error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected internal server error occurred.",
        status_code=500,
    )


# 4. Health Checks
@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe: returns 200 when service is running."""
    return success_response({"status": "healthy"})


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe: verifies backend dependencies and scheduler health."""
    sched = get_scheduler()
    return success_response({
        "status": "ready",
        "scheduler_running": sched.running,
        "environment": settings.APP_ENV,
        "version": "1.0.0",
    })


# 5. Include API Routers under /api/v1
prefix = settings.API_PREFIX

app.include_router(auth.router, prefix=prefix)
app.include_router(users.router, prefix=prefix)
app.include_router(lists.router, prefix=prefix)
app.include_router(todos.router, prefix=prefix)
app.include_router(tags.router, prefix=prefix)
app.include_router(timetable.router, prefix=prefix)
app.include_router(subjects.router, prefix=prefix)
app.include_router(assignments.router, prefix=prefix)
app.include_router(exams.router, prefix=prefix)
app.include_router(hackathons.router, prefix=prefix)
app.include_router(certifications.router, prefix=prefix)
app.include_router(internships.router, prefix=prefix)
app.include_router(projects.router, prefix=prefix)
app.include_router(events.router, prefix=prefix)
app.include_router(reminders.router, prefix=prefix)
app.include_router(notifications.router, prefix=prefix)
app.include_router(attachments.router, prefix=prefix)
app.include_router(calendar.router, prefix=prefix)
app.include_router(dashboard.router, prefix=prefix)
app.include_router(search.router, prefix=prefix)
app.include_router(analytics.router, prefix=prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.is_production,
    )
