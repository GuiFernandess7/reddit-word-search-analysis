import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.post import Base

class SQLiteDatabase:
    def __init__(self, db_directory: str = None, db_name: str = 'posts.db'):
        if db_directory is None:
            db_directory = os.path.join(os.path.dirname(__file__), 'data')

        os.makedirs(db_directory, exist_ok=True)

        self.db_url = f"sqlite:///{os.path.join(db_directory, db_name)}"
        self.engine = create_engine(self.db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def close(self):
        self.engine.dispose()
