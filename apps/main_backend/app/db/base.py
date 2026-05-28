from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import model modules so Alembic can discover metadata.
from app import models  # noqa: E402,F401
