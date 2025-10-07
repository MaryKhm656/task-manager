from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.web import routes


def create_app(is_gui: bool = False) -> FastAPI:
    app = FastAPI(title="Task Scheduler", log_level="debug")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.state.is_gui = is_gui

    @app.middleware("http")
    async def detect_gui(request: Request, call_next):
        is_gui_flag = False
        if request.headers.get("X-App-Client") == "GUI":
            is_gui_flag = True
        elif request.cookies.get("is_gui") == "1":
            is_gui_flag = True
        elif request.query_params.get("gui") == "1":
            is_gui_flag = True

        request.state.is_gui = is_gui_flag

        response = await call_next(request)

        if is_gui_flag and not request.cookies.get("is_gui"):
            secure_flag = request.url.scheme == "https"
            response.set_cookie(
                key="is_gui",
                value="1",
                max_age=60 * 60 * 24 * 30,
                httponly=True,
                samesite="lax",
                secure=secure_flag,
            )

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

    @app.get("/web-launch")
    async def web_launch(request: Request):
        resp = RedirectResponse(url="/")
        resp.delete_cookie("is_gui")
        return resp

    app.include_router(routes.router)
    return app
