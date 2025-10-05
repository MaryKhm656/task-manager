import webview
from dotenv import load_dotenv

load_dotenv()  # noqa: E402


SERVER_URL = "http://194.39.101.101:8000"

if __name__ == "__main__":
    window = webview.create_window(
        "Планировщик задач",
        f"{SERVER_URL}/?gui=1",
        width=1500,
        height=900,
        min_size=(800, 600),
    )
    webview.start()
