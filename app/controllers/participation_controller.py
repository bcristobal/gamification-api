from sqlmodel import Session
from datetime import datetime
from fastapi import HTTPException
from sqlmodel import select
from ..models import participation_model as model
import uuid
from ..models.user_model import User
from ..controllers.game_controller import get_game_by_name
from ..controllers.challenge_controller import get_challenge_by_id

def create_participation (game_name: str, challenge_id: uuid.UUID,new_participation: model.ParticipationCreate , user: User, session: Session) -> model.Participation:
    game = get_game_by_name(game_name, session)
    challenge = get_challenge_by_id(challenge_id, session)
    if game.id != challenge.game_id:
        raise HTTPException(status_code=400, detail="Game and challenge doesn't match.")
    
    points = calculate_init_points(new_participation.dificulty, challenge.points)
    
    participation = model.Participation(**new_participation.model_dump(),
                                        user_id=user.id,
                                        challenge_id=challenge_id,
                                        game_id=game.id,
                                        needed_points=points)
    session.add(participation)
    session.commit()
    session.refresh(participation)
    return participation
    


def calculate_init_points(dificulty: model.Dificulty, points: int) -> int:
    if dificulty == model.Dificulty.EASY:
        return points
    elif dificulty == model.Dificulty.MEDIUM:
        return points + 1000
    elif dificulty == model.Dificulty.HARD:
        return points + 3000


def get_participations(game_name: str, challenge_id: uuid.UUID, user: User, session: Session) -> list[model.Participation]:
    game = get_game_by_name(game_name, session)
    challenge = get_challenge_by_id(challenge_id, session)
    if game.id != challenge.game_id:
        raise HTTPException(status_code=400, detail="Game and challenge doesn't match.")
    
    stm = select(model.Participation).where(model.Participation.user_id == user.id, model.Participation.game_id == game.id)
    participations = session.exec(statement=stm).all()

    return participations


def get_participation_by_id(id: uuid.UUID, session: Session) -> model.Participation:
    participation = session.exec(
        select(model.Participation).where(model.Participation.id == id)
    ).first()
    if not participation:
        raise HTTPException(status_code=404, detail="Participation not found.")
    return participation

def add_points(game_name: str, challenge_id: uuid.UUID, participation_id: uuid.UUID,participation_add_points: model.ParticipationAddPoints, user: User, session: Session) -> model.Participation:
    game = get_game_by_name(game_name, session)
    challenge = get_challenge_by_id(challenge_id, session)
    participation = get_participation_by_id(participation_id, session)


    if game.id != challenge.game_id:
        raise HTTPException(status_code=400, detail="Game and challenge doesn't match.")
    if participation.game_id != game.id:
        raise HTTPException(status_code=400, detail="Game and participation doesn't match.")
    if participation.challenge_id != challenge.id:
        raise HTTPException(status_code=400, detail="Challenge and participation doesn't match.")
    
    participation.total_points = participation.total_points + participation_add_points.points

    session.commit()
    session.refresh(participation)
    return participation
    
    
