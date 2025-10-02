import os
import threading
import time

os.environ["GUI_MODE"] = "true"

import uvicorn
import webview
from dotenv import load_dotenv

load_dotenv()  # noqa: E402

from app.web.main import create_app


def run_server():
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


def wait_for_server():
    """Ожидание запуска сервера"""
    import requests

    for i in range(10):
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=2)
            if response.status_code == 200:
                return True
        except Exception:
            time.sleep(0.5)
    return False


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    if wait_for_server():
        window = webview.create_window(
            "Планировщик задач",
            "http://127.0.0.1:8000",
            width=1500,
            height=900,
            min_size=(800, 600),
        )
        webview.start()
    else:
        print("Не удалось запустить сервер. Проверьте настройки.")
