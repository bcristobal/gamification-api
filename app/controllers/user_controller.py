from fastapi import HTTPException
from sqlmodel import select
from sqlmodel import Session
from ..auth import get_password_hash
from ..models import user_model as model

def get_user_by_username(username: str, session: Session) -> model.User:
    user = session.exec(
        statement=select(model.User).where(model.User.username == username)
        ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


def create_user(new_user: model.UserCreate, session: Session) -> model.User:
    # Check if email is already in use
    user_check = session.exec(
        statement=select(model.User).where(model.User.email == new_user.email)
    ).first()
    if user_check:
        raise HTTPException(status_code=400, detail="Email is already in use.")

    # Check if username is already in use
    user_check = session.exec(
        statement=select(model.User).where(model.User.username == new_user.username)
    ).first()
    if user_check:
        raise HTTPException(status_code=400, detail="Username is already in use.")
    
    hashed_password = get_password_hash(new_user.password)
    user = model.User(**new_user.model_dump(),
                        hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(updated_user: model.UserUpdate, user: model.User, session: Session) -> model.User:
    # Update the username
    if updated_user.username:
        user_check = session.exec(
            statement=select(model.User).where(model.User.username == updated_user.username)
        ).first()
        if user_check:
            raise HTTPException(status_code=400, detail="Username is already in use.")
        user.username = updated_user.username
    
    # Update the password
    if updated_user.password:
        user.hashed_password = get_password_hash(updated_user.password)

    session.commit()
    session.refresh(user)
    return user


def delete_user(user: model.User, session: Session) -> model.User:
    session.delete(user)
    session.commit()
    return user
    