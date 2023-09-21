from fastapi import FastAPI
from routes.routes import report_router

app = FastAPI()

app.include_router(report_router)
