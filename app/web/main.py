from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.web import routes


def create_app(is_gui: bool = False) -> FastAPI:
    """
    Factory for creating a FastAPI FlapTask application

    args:
    is_gui: Flag indicating that the application is running in GUI mode

    returns:
    FastAPI: Configured FastAPI application with routes and middleware
    """
    app = FastAPI(title="FlapTask", log_level="debug")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.state.is_gui = is_gui

    @app.middleware("http")
    async def detect_gui(request: Request, call_next):
        """
        Middleware for determining and managing the GUI mode.

        Determines the application's operating mode (GUI/Web) based on:
        - X-App-Client header
        - is_gui cookie
        - gui query parameter

        Sets the appropriate cookies to save the mode
        """
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
            response.set_cookie(
                key="is_gui",
                value="1",
                max_age=60 * 60 * 24 * 30,
                httponly=True,
                samesite="lax",
                secure=False,
            )

        return response

    @app.get("/gui-launch")
    async def gui_launch(request: Request):
        """
        Endpoint for forced switching to GUI mode.

        Sets the is_gui cookie and redirects to the home page.

        returns:
        RedirectResponse: Redirects to the home page with the cookie set.
        """
        resp = RedirectResponse(url="/")
        resp.set_cookie(
            key="is_gui",
            value="1",
            max_age=60 * 60 * 24 * 30,
            httponly=True,
            samesite="lax",
            secure=False,
        )
        return resp

    @app.get("/web-launch")
    async def web_launch(request: Request):
        """
        Endpoint for forced switching to Web mode.

        Deletes the is_gui cookie and redirects to the home page.

        returns:
        RedirectResponse: Redirect to the home page with the cookie deleted.
        """
        resp = RedirectResponse(url="/")
        resp.delete_cookie("is_gui")
        return resp

    app.include_router(routes.router)
    return app
