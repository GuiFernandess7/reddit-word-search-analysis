from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

db_directory = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(db_directory, exist_ok=True)

DATABASE_URL = f'sqlite:///{os.path.join(db_directory, "posts.db")}'
engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

