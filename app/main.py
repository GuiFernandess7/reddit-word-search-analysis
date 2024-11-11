import logging
import os

from app.settings import SERVICE_ACCOUNT_FILE, SCOPES, FOLDER_ID, USER_AGENT, INITIAL_PARAMS
from app.database import SQLiteDatabase
from app.services.reddit_service import RedditFacade
from app.services.post_service import PostService
from app.services.drive_service import GoogleDriveAuth, FileUploader

subreddit = 'brasilivre'
sqlite_filename = 'posts.db'

def main():
    db_path = os.path.join(os.path.dirname(__file__), 'data', sqlite_filename)
    db = SQLiteDatabase(db_directory=os.path.dirname(db_path), db_name=sqlite_filename)
    reddit_facade = RedditFacade(user_agent=USER_AGENT, initial_params=INITIAL_PARAMS)

    try:
        with db.get_session() as session:
            post_service = PostService(session)
            filtered_posts = reddit_facade.get_filtered_posts(subreddit=subreddit, search_phrase='mbl')

            if filtered_posts:
                logger.info(f"[PROCESSING] {len(filtered_posts)} new posts from {filtered_posts[0].ts} to {filtered_posts[-1].ts}")
                post_service.save_posts(filtered_posts)
                logger.info(f"Subreddit posts '{subreddit}' saved successfully!")
            else:
                logger.info(f"No posts found in subreddit '{subreddit}' with the phrase 'mbl'.")

    except Exception as e:
        logger.error(f"Error saving posts in database: {e}")
        return

    try:
        drive_auth = GoogleDriveAuth(SERVICE_ACCOUNT_FILE, SCOPES)
        drive_auth.authenticate()
        file_manager = FileUploader(drive_auth.drive_service)
        file_manager.upload(db_filepath=db_path, db_filename=sqlite_filename, folder_id=FOLDER_ID)
        logger.info(f"[SUCCESS] - SQLite file '{sqlite_filename}' sent to google drive.")

    except Exception as e:
        logger.error(f"Google Drive upload error: {e}")
        return

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] - [%(levelname)s] - %(message)s'
    )
    logger = logging.getLogger(__name__)
    main()
