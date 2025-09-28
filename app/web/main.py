from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.web import routes


def create_app(is_gui: bool = False) -> FastAPI:
    """Application entry point"""
    app = FastAPI(title="Task Scheduler", log_level="debug")

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.state.is_gui = is_gui

    @app.exception_handler(401)
    async def unauthorized_handler(request: Request, exc: HTTPException):
        return RedirectResponse(url="/", status_code=302)

    app.include_router(routes.router)

    return app
