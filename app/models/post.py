from sqlalchemy import Column, BigInteger, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class PostModel(Base):
    __tablename__ = 'posts'

    ts = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=False)
    has_label = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    subreddit = Column(String, nullable=True)

    def __repr__(self):
        return f"<Post(ts={self.ts}, title='{self.title}', has_label='{self.has_label}', created_at={self.created_at})>"
