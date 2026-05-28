from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


@lru_cache()
def get_engine():
    return create_engine(settings.database_url)


def get_db():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
