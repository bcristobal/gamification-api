from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated
import uuid
from ..db import get_session
from ..models import achievement_model as model
from ..auth import decode_token
from ..controllers import achievement_controller as controller

router = APIRouter(tags=["achievements"])

@router.post("/achievements")
def create_achievement(*,
                      new_achievement: model.AchievementCreate,
                      my_user: Annotated[dict, Depends(decode_token)],
                      session: Session = Depends(get_session)):
    return controller.create_achievement(new_achievement, my_user, session)

@router.get("/achievements")
def get_all_achievements(*,
                        session: Session = Depends(get_session)):
    return controller.get_all_achievements(session)

@router.get("/achievements/{achievement_id}")
def get_achievement(*,
                   achievement_id: uuid.UUID,
                   session: Session = Depends(get_session)):
    return controller.get_achievement_by_id(achievement_id, session)

@router.get("/users/me/achievements")
def get_my_achievements(*,
                       my_user: Annotated[dict, Depends(decode_token)],
                       session: Session = Depends(get_session)):
    return controller.get_user_achievements(my_user, session)

