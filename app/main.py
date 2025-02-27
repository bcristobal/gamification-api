from fastapi import FastAPI

from .db import init_db
from .auth import auth_router
from .views.user_view import router as user_router
from .views.game_view import router as game_router
from .views.challenge_view import router as challenge_router

app = FastAPI()

@app.on_event("startup")
def on_start_up():
   init_db()

@app.get("/")
def root ():
    return {"message": "The server is running."}

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(game_router)
app.include_router(challenge_router)

