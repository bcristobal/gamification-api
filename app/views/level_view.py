from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated
import uuid
from ..db import get_session
from ..models import level_model as model
from ..auth import decode_token
from ..controllers import level_controller as controller

router = APIRouter(tags=["levels"])

@router.post("/levels")
def create_level(*,
                new_level: model.LevelCreate,
                my_user: Annotated[dict, Depends(decode_token)],
                session: Session = Depends(get_session)):
    return controller.create_level(new_level, my_user, session)

@router.get("/levels")
def get_all_levels(*,
                  session: Session = Depends(get_session)):
    return controller.get_all_levels(session)

@router.get("/levels/{level_number}")
def get_level_by_number(*,
                       level_number: int,
                       session: Session = Depends(get_session)):
    return controller.get_level_by_number(level_number, session)

