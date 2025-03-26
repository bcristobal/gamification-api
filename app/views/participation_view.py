from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated
import uuid
from ..db import get_session
from ..models import participation_model as model
from ..auth import decode_token
from ..controllers import participation_controller as controller

router = APIRouter(tags=["participations"])

@router.post("/games/{game_name}/challenges/{challenge_id}/participations")
def create_participation(*,
                         game_name: str,
                         challenge_id: uuid.UUID,
                         new_participation: model.ParticipationCreate,
                         my_user: Annotated[dict, Depends(decode_token)],
                         session: Session = Depends(get_session)):
    return controller.create_participation(game_name=game_name, challenge_id=challenge_id, new_participation=new_participation, user=my_user, session=session)


@router.get("/games/{game_name}/challenges/{challenge_id}/participations")
def get_participations(*,
                       game_name: str,
                       challenge_id: uuid.UUID,
                       my_user: Annotated[dict, Depends(decode_token)],
                       session: Session = Depends(get_session)
                       ):
    return controller.get_participations(game_name=game_name, challenge_id=challenge_id, user=my_user, session=session)


@router.post("/games/{game_name}/challenges/{challenge_id}/participations/{participation_id}/points")
def add_points(*,
               game_name: str,
               challenge_id: uuid.UUID,
               participation_id: uuid.UUID,
               participation_add_points: model.ParticipationAddPoints,
               my_user: Annotated[dict, Depends(decode_token)],
               session: Session = Depends(get_session)):
    return controller.add_points(game_name, challenge_id, participation_id, participation_add_points, my_user, session)

@router.get("/games/{game_name}/my-challenges")
def get_user_challenges(*,
                       game_name: str,
                       my_user: Annotated[dict, Depends(decode_token)],
                       session: Session = Depends(get_session)
                       ):
    """
    Obtiene todos los desafíos en los que el usuario está participando para un juego específico
    """
    return controller.get_user_challenges_by_game(game_name=game_name, user=my_user, session=session)