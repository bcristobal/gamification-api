from fastapi import HTTPException
from sqlmodel import select
from sqlmodel import Session
from ..models import game_model as model
from ..models.user_model import User

def get_game_by_name(name: str, session: Session) -> model.Game:
    game = session.exec(
        statement=select(model.Game).where(model.Game.name == name)
    ).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found.")
    return game


def create_game(new_game: model.GameCreate, creator: User, session: Session) -> model.Game:
    if creator.is_admin:
        game_check = session.exec(
            statement=select(model.Game).where(model.Game.name == new_game.name)
        ).first()
        if game_check:
            raise HTTPException(status_code=400, detail="Name is already in use.")
        
        game = model.Game(
            name=new_game.name,
            description=new_game.description,
            strategy=new_game.strategy,
            creator_id=creator.id,
            )
        
        session.add(game)
        session.commit()
        session.refresh(game)
        return game
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
    

def update_game(game_name: str, updated_game: model.GameUpdate, user: User, session: Session) -> model.Game:
    if user.is_admin:
        game = get_game_by_name(name=game_name, session=session)

        if user.id != game.creator_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if updated_game.name:
            game_check = session.exec(
                statement=select(model.Game).where(model.Game.name == updated_game.name)
                ).first()
            if game_check:
                raise HTTPException(status_code=400, detail="Name is already in use.")
            game.name = updated_game.name
        
        if updated_game.description:
            game.description = updated_game.description

        if updated_game.strategy:
            game.strategy = updated_game.strategy
            
        session.commit()
        session.refresh(game)
        return game
     
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

def delete_game(game_name:str, user: User, session: Session) -> model.Game:
    if user.is_admin:
        game = get_game_by_name(name=game_name, session=session)

        if user.id != game.creator_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        session.delete(game)
        session.commit()
        return game

            