from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated
import uuid
from ..db import get_session
from ..models import challenge_model as model
from ..auth import decode_token
from ..controllers import challenge_controller as controller

router = APIRouter(tags=["challenges"])

@router.post("/games/{game_name}/challenges")
def create_challenge(*,
                     game_name: str,
                     new_challenge: model.ChallengeCreate,
                     my_user: Annotated[dict, Depends(decode_token)],
                     session: Session = Depends(get_session)
                     ):
    return controller.create_challenge(game_name=game_name, new_challenge=new_challenge, creator=my_user, session=session)


@router.get("/games/{game_name}/challenges")
def get_all_challenges(*,
                       game_name: str,
                       skip: int = 0,
                       limit: int = 4,
                       status: str = "all",
                       session: Session = Depends(get_session)):
    return controller.get_all_challenges(game_name=game_name, status=status, skip=skip, limit=limit, session=session)
    

@router.get("/games/{game_name}/challenges/{challenge_id}")
def get_challenge(*,
                  game_name: str,
                  challenge_id: uuid.UUID,
                  session: Session = Depends(get_session)):
    return controller.get_challenge_by_id(id=challenge_id, session=session)


@router.put("/games/{game_name}/challenges/{challenge_id}")
def update_challenge(*,
                     game_name: str,
                     challenge_id: uuid.UUID,
                     updated_challenge: model.ChallengeUpdate,
                     my_user: Annotated[dict, Depends(decode_token)],
                     session: Session = Depends(get_session)):
    return controller.update_challenge(game_name, challenge_id, updated_challenge, my_user, session)


@router.delete("/games/{game_name}/challenges/{challenge_id}")
def delete_challenge(*,
                     game_name: str,
                     challenge_id: uuid.UUID,
                     my_user: Annotated[dict, Depends(decode_token)],
                     session: Session = Depends(get_session)):
    return controller.delete_challenge(game_name=game_name, challenge_id=challenge_id, creator=my_user, session=session)