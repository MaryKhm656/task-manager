import os

from dotenv import load_dotenv

load_dotenv()  # noqa: E402

from app.web.main import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.1.1.1"),
        port=int(os.getenv("PORT", 8000)),
    )
