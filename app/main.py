from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, like, follow, comment
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://localhost", "http://localhost:8080", "http://localhost:5173", "http://localhost:4173", "https://social-ui-production.up.railway.app:8080"]

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
