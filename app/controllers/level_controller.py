from sqlmodel import Session, select
from fastapi import HTTPException
from ..models.user_model import User
from ..models import level_model as model
import uuid

def create_level(new_level: model.LevelCreate, admin: User, session: Session) -> model.Level:
    if not admin.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Validate level ranges don't overlap
    existing_levels = session.exec(select(model.Level)).all()
    for level in existing_levels:
        if (new_level.min_xp <= level.max_xp and new_level.max_xp >= level.min_xp):
            raise HTTPException(status_code=400, detail=f"Level range overlaps with existing level {level.number}.")
    
    level = model.Level(**new_level.model_dump())
    session.add(level)
    session.commit()
    session.refresh(level)
    return level

def get_level_by_number(number: int, session: Session) -> model.Level:
    level = session.exec(
        select(model.Level).where(model.Level.number == number)
    ).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found.")
    return level

def get_level_for_xp(xp: int, session: Session) -> model.Level:
    levels = session.exec(
        select(model.Level).where(
            model.Level.min_xp <= xp,
            model.Level.max_xp >= xp
        )
    ).all()
    
    if not levels:
        # If no matching level, get the highest level
        highest_level = session.exec(
            select(model.Level).order_by(model.Level.number.desc())
        ).first()
        return highest_level
    
    return levels[0]

def update_user_level(user: User, session: Session) -> User:
    appropriate_level = get_level_for_xp(user.xp_points, session)
    user.level_id = appropriate_level.id
    session.commit()
    session.refresh(user)
    return user

def get_all_levels(session: Session) -> list[model.Level]:
    return session.exec(
        select(model.Level).order_by(model.Level.number)
    ).all()

