from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from app.web import routes


def create_app(is_gui: bool = False) -> FastAPI:
    app = FastAPI(title="Task Scheduler", log_level="debug")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.state.is_gui = is_gui

    @app.middleware("http")
    async def detect_gui(request: Request, call_next):
        if request.cookies.get("is_gui") == "1":
            request.state.is_gui = True
        else:
            request.state.is_gui = False

        response = await call_next(request)
        return response

    @app.get("/gui-launch")
    async def gui_launch(request: Request):
        resp = RedirectResponse(url="/")
        secure_flag = request.url.scheme == "https"
        resp.set_cookie(
            key="is_gui",
            value="1",
            max_age=60 * 60 * 24 * 30,
            httponly=True,
            samesite="lax",
            secure=secure_flag,
        )
        return resp

    app.include_router(routes.router)
    return app
