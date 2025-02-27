from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi.exceptions import HTTPException
from jose import jwt
from passlib.hash import argon2
from sqlmodel import select
from .models.user_model import User
from .db import get_session
from sqlmodel import Session

SECRET_KEY = "SDLKFJSFLKSDJFL"
ALGORITHM = "HS256"

auth_router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return argon2.verify(plain_password, hashed_password)

def get_password_hash(password):
    return argon2.hash(password)

def encode_token(payload: dict) -> str:
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return token

def decode_token(token: Annotated[str, Depends(oauth2_scheme)], session: Session=Depends(get_session)) -> dict:
    data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(data)
    stm = select(User).where(User.username == data["username"])
    user = session.exec(statement=stm).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@auth_router.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session=Depends(get_session)):
    stm = select(User).where(User.username == form_data.username)
    user = session.exec(statement=stm).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password.")
    token = encode_token({"username": user.username, "email": user.email})
    return {"access_token": token, "token_type": "bearer"}