from collections.abc import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.config import config

db_engine = create_engine(config.POSTGRES_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)

def get_db() -> Iterator[Session]:
    with SessionLocal() as db:
        yield db
