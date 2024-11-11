from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

class PostService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def save_posts(self, posts):
        try:
            for post in posts:
                self.db_session.merge(post)
            self.db_session.commit()

        except IntegrityError as e:
            self.db_session.rollback()
            raise Exception(f"Erro de integridade: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise e
