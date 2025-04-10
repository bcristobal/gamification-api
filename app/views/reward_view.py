from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated
import uuid
from ..db import get_session
from ..models import reward_model as model
from ..auth import decode_token
from ..controllers import reward_controller as controller

router = APIRouter(tags=["rewards"])

@router.post("/rewards")
def create_reward(*,
                 new_reward: model.RewardCreate,
                 my_user: Annotated[dict, Depends(decode_token)],
                 session: Session = Depends(get_session)):
    return controller.create_reward(new_reward, my_user, session)

@router.get("/rewards")
def get_all_rewards(*,
                   session: Session = Depends(get_session)):
    return controller.get_all_rewards(session)

@router.get("/rewards/{reward_id}")
def get_reward(*,
              reward_id: uuid.UUID,
              session: Session = Depends(get_session)):
    return controller.get_reward_by_id(reward_id, session)

@router.get("/users/me/rewards")
def get_my_rewards(*,
                  my_user: Annotated[dict, Depends(decode_token)],
                  session: Session = Depends(get_session)):
    return controller.get_user_rewards(my_user, session)

@router.get("/users/me/available-rewards")
def get_available_rewards(*,
                         my_user: Annotated[dict, Depends(decode_token)],
                         session: Session = Depends(get_session)):
    return controller.get_available_rewards(my_user, session)

@router.post("/rewards/{reward_id}/claim")
def claim_reward(*,
                reward_id: uuid.UUID,
                my_user: Annotated[dict, Depends(decode_token)],
                session: Session = Depends(get_session)):
    return controller.claim_reward(my_user, reward_id, session)

@router.post("/users/me/rewards/{user_reward_id}/use")
def use_reward(*,
              user_reward_id: uuid.UUID,
              my_user: Annotated[dict, Depends(decode_token)],
              session: Session = Depends(get_session)):
    return controller.use_reward(my_user, user_reward_id, session)

