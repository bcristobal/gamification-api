from sqlmodel import Session
from datetime import datetime
from fastapi import HTTPException
from sqlmodel import select
from ..models.user_model import User
from ..models.game_model import Game
from ..models import challenge_model as model
from ..controllers.game_controller import get_game_by_name
import uuid

def validate_dates(start_date: datetime, finish_date: datetime):
    if start_date > finish_date:
        raise HTTPException(status_code=400, detail="Finish date must be greater than start date.")
    
def validate_points(points: int):
    if points < 0:
        raise HTTPException(status_code=400, detail="Points must be greater than 0.")
    

def create_challenge(game_name: str, new_challenge: model.ChallengeCreate, creator: User, session: Session) -> model.Challenge:
    if creator.is_admin:
        game = get_game_by_name(name=game_name, session=session)
        if game.creator_id != creator.id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        validate_dates(new_challenge.start_date, new_challenge.finish_date)
        validate_points(new_challenge.points)

        challenge = model.Challenge(**new_challenge.model_dump(), game_id=game.id)

        session.add(challenge)
        session.commit()
        session.refresh(challenge)
        return challenge
    else: 
        raise HTTPException(status_code=401, detail="Unauthorized")
    

def get_all_challenges(game_name: str, status: str, skip: int, limit: int, session: Session) -> list[model.Challenge]:
    game = session.exec(
        statement=select(Game).where(Game.name == game_name)
    ).first()

    stm = select(model.Challenge)
    if status == "upcoming":
        stm = stm.where(model.Challenge.start_date > datetime.now(), model.Challenge.game_id == game.id)
    elif status == "past":
        stm = stm.where(model.Challenge.finish_date < datetime.now(), model.Challenge.game_id == game.id)
    elif status == "ongoing":
        stm = stm.where(model.Challenge.start_date < datetime.now(), model.Challenge.finish_date > datetime.now(), model.Challenge.game_id == game.id)
    
    stm = stm.order_by(model.Challenge.finish_date).offset(skip).limit(limit)
    
    challenges = session.exec(stm).all()
    
    return challenges


def get_challenge_by_id(id: uuid.UUID, session: Session) -> model.Challenge:
    challenge = session.exec(
        statement=select(model.Challenge).where(model.Challenge.id == id)
    ).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")
    return challenge


def update_challenge(game_name: str, challenge_id:uuid.UUID, updated_challenge: model.ChallengeUpdate, creator: User, session: Session) -> model.Challenge:
    if creator.is_admin:
        game = get_game_by_name(name=game_name, session=session)
        if game.creator_id != creator.id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        challenge = get_challenge_by_id(id=challenge_id, session=session)

        if updated_challenge.name:
            challenge.name = updated_challenge.name

        if updated_challenge.description:
            challenge.description = updated_challenge.description

        if updated_challenge.start_date and updated_challenge.finish_date:
            validate_dates(updated_challenge.start_date, updated_challenge.finish_date)
            challenge.start_date = updated_challenge.start_date
            challenge.finish_date = updated_challenge.finish_date
        elif updated_challenge.start_date:
            validate_dates(updated_challenge.start_date, challenge.finish_date)
            challenge.start_date = updated_challenge.start_date
        elif updated_challenge.finish_date:
            validate_dates(challenge.start_date, updated_challenge.finish_date)
            challenge.finish_date = updated_challenge.finish_date

        if updated_challenge.points:
            validate_points(updated_challenge.points)
            challenge.points = updated_challenge.points

        if updated_challenge.type:
            challenge.type = updated_challenge.type
        session.commit()
        session.refresh(challenge)
        return challenge


def delete_challenge(game_name:str,challenge_id:uuid.UUID , creator: User, session: Session) -> model.Challenge:
    if creator.is_admin:

        game = get_game_by_name(game_name, session)
        if game.creator_id != creator.id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        challenge = get_challenge_by_id(challenge_id, session)
        session.delete(challenge)
        session.commit()
        return challenge

