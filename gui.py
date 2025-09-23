import threading

import uvicorn
import webview
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.web import routes


def run_server():
    load_dotenv()

    app = FastAPI(title="Task Scheduler", log_level="debug")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.include_router(routes.router)

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    window = webview.create_window(
        "Планировщик задач", "http://127.0.0.1:8000", width=1200, height=800
    )
    webview.start()
