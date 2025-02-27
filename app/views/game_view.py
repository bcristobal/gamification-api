from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated
from ..db import get_session
from ..models import game_model as model
from ..auth import decode_token
from ..controllers import game_controller as controller

router = APIRouter(prefix="/games", tags=["games"])

@router.post("/")
def create_gam(*,
                new_game: model.GameCreate,
                my_user: Annotated[dict, Depends(decode_token)],
                session: Session = Depends(get_session)):
    return controller.create_game(new_game=new_game, creator=my_user, session=session)

@router.get("/{game_name}")
def get_game(*,
            game_name: str,
            session: Session = Depends(get_session)):
    return controller.get_game_by_name(name=game_name, session=session)

@router.put("/{game_name}")
def update_game(*,
                game_name: str,
                updated_game: model.GameUpdate,
                my_user: Annotated[dict, Depends(decode_token)],
                session: Session = Depends(get_session)):
    return controller.update_game(game_name=game_name, updated_game=updated_game, user=my_user, session=session)

@router.delete("/{game_name}")
def delete_game(*,
                game_name: str,
                my_user: Annotated[dict, Depends(decode_token)],
                session: Session = Depends(get_session)):
    return controller.delete_game(game_name=game_name, user=my_user, session=session)
