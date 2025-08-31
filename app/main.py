from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import post, user, auth, like, follow, comment, chat
from fastapi.middleware.cors import CORSMiddleware

# nice app
app = FastAPI()

origins = ["http://localhost", "http://localhost:8080", "http://localhost:5173", "http://localhost:4173", "social-core-production.up.railway.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(like.router)
app.include_router(follow.router)
app.include_router(comment.router)
app.include_router(chat.router)