"""Точка входа FastAPI-приложения: инициализация, middleware и подключение роутеров."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import lifespan
from src.routes import alerts, files

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router)
app.include_router(alerts.router)
