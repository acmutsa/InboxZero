from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config


def add_cors_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get_cors_list,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )