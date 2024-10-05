# Reddit Automated Data Collection

![reddit-cover](https://github.com/user-attachments/assets/c8db4cf8-89cb-4440-9732-531b110e4f2b)

## Introduction

The application is designed to automate the process of collecting, processing, and storing data from a specific subreddit on Reddit. By leveraging Google Drive for storage and utilizing OAuth for authentication, the application efficiently manages posts, allowing users to maintain a database of relevant information while ensuring data integrity and accessibility.
Functionality

- Google Drive Authentication: The application uses a service account to authenticate with Google Drive. This allows it to upload and update files securely in a specified folder, ensuring that the latest data is always available.

- Data Collection from Reddit: The application retrieves the latest posts from a specified subreddit using the Reddit API. It constructs request headers that include an OAuth token for secure access.

- Post Processing: Each post is processed to check for specific keywords. The application creates Post objects containing relevant data such as timestamps, titles, and labels based on keyword presence.

- Database Interaction: The application connects to a SQLite database using SQLAlchemy. It checks for existing posts to prevent duplication before inserting new entries. If there are new posts, they are added to the database, ensuring that only unique records are stored.

- File Upload to Google Drive: After inserting new data into the database, the application uploads the updated SQLite file to Google Drive, replacing the previous version if it exists. This ensures that users always have access to the most current data.

- Logging and Error Handling: The application includes robust logging mechanisms to track the process flow and capture any errors that occur. This helps in debugging and maintaining the application effectively.

## Conclusion

By automating the collection and storage of Reddit posts, the application provides a seamless experience for users looking to analyze and manage data from social media. With its integrated logging and error handling, users can rely on it to operate smoothly while they focus on deriving insights from the collected data.
