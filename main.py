from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import routes, template_routes


app = FastAPI(title="Task Scheduler", log_level="debug")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(routes.router)
app.include_router(template_routes.router)