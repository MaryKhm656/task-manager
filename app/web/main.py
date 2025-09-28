from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.web import routes


def create_app() -> FastAPI:
    """Application entry point"""
    app = FastAPI(title="Task Scheduler", log_level="debug")

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.include_router(routes.router)

    return app
