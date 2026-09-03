from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth_routes import router as auth_router
from app.api.history_routes import router as history_router
from app.api.routes import router
from app.config import settings
from app.db import init_db

app = FastAPI(
    title=settings.app_name,
    description="AI-Driven Hyper-Local Business Advisory and Financial Structuring "
                "Assistant for Rural Micro-Entrepreneurs (SIH26091)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(history_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "GramVyapaar AI backend is running. See /docs for API reference."}
