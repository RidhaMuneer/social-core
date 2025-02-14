# Social Media API

Welcome to the Social Media API! This RESTful API allows users to interact on a social media platform. Users can post content, like posts, comment on posts, follow other users, and receive follow suggestions. It also includes user authentication and protected routes using JWT tokens. Images uploaded by users are stored in AWS S3.

## Features

- **User Authentication**: Register, login, and manage user sessions using JWT tokens.
- **Post Management**: Create, read, update, and delete posts.
- **Like Posts**: Users can like posts to express their appreciation.
- **Comment on Posts**: Users can comment on posts to express their appreciation.
- **Follow Users**: Follow other users to see their posts and updates.
- **Follow Suggestions**: Get suggestions on users to follow based on your current follow list.
- **View User Status**: See how many followers and followings a user has.
- **Image Storage**: User-uploaded images are securely stored in AWS S3.
- **Protected Routes**: Access to certain routes is restricted to authenticated users with valid JWT tokens.

## Tech Stack

- **Backend**: Python
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Image Storage**: AWS S3
- **Authentication**: JWT (JSON Web Tokens)

## Setup and Installation

### Prerequisites

- Python 3.8 or later
- PostgreSQL
- AWS S3 account

### Installation

1. **Clone the Repository**:
   ```bash
   git clone git@github.com:RidhaMuneer/social-core.git
   cd social-core
    ```

2. **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Check the app/config.py file to see what environment variables are needed, put them in a .env file**

5. **Start the server**:
    ```bash
    uvicorn app.main:app --reload
    ```

6. **Check Swagger UI for endpoints documentation**