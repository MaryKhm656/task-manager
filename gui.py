import requests
import webview
from dotenv import load_dotenv

load_dotenv()  # noqa: E402


SERVER_URL = "http://194.39.101.101:8000/"


def check_server_connection():
    """Проверяем подключение к серверу"""
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"Сервер ответил с ошибкой: {response.status_code}")
            return False
    except Exception as e:
        print(f"Не удалось подключиться к серверу: {e}")
        return False


if __name__ == "__main__":
    window = webview.create_window(
        "Планировщик задач",
        SERVER_URL,
        width=1500,
        height=900,
        min_size=(800, 600),
    )
    webview.start()
