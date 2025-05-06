# app/db/database.py

from sqlmodel import SQLModel, create_engine, Session
from app.core.configuration import settings

DATABASE_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session


# def init_db():
#     with engine.begin() as connect:
#         await connect.run_sync(SQLModel.metadata.create_all)
def init_db():
    SQLModel.metadata.create_all(engine)