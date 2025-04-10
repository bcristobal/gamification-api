from sqlmodel import Session, select
from datetime import datetime
from fastapi import HTTPException
from ..models.user_model import User
from ..models import reward_model as model
import uuid

def create_reward(new_reward: model.RewardCreate, admin: User, session: Session) -> model.Reward:
    if not admin.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    reward = model.Reward(**new_reward.model_dump())
    session.add(reward)
    session.commit()
    session.refresh(reward)
    return reward

def get_reward_by_id(id: uuid.UUID, session: Session) -> model.Reward:
    reward = session.exec(
        select(model.Reward).where(model.Reward.id == id)
    ).first()
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found.")
    return reward

def get_all_rewards(session: Session) -> list[model.Reward]:
    return session.exec(select(model.Reward)).all()

def get_available_rewards(user: User, session: Session) -> list[model.Reward]:
    """Get rewards that the user has enough points for but hasn't claimed yet"""
    all_rewards = get_all_rewards(session)
    
    # Get rewards user has already claimed
    claimed_rewards = session.exec(
        select(model.UserReward).where(model.UserReward.user_id == user.id)
    ).all()
    claimed_reward_ids = [r.reward_id for r in claimed_rewards]
    
    # Filter for available rewards
    available_rewards = []
    for reward in all_rewards:
        if reward.id not in claimed_reward_ids and user.total_points >= reward.required_points:
            available_rewards.append(reward)
    
    return available_rewards

def claim_reward(user: User, reward_id: uuid.UUID, session: Session) -> model.UserReward:
    reward = get_reward_by_id(id=reward_id, session=session)
    
    # Check if user has enough points
    if user.total_points < reward.required_points:
        raise HTTPException(status_code=400, detail="Not enough points to claim this reward.")
    
    # Check if user has already claimed this reward
    existing = session.exec(
        select(model.UserReward).where(
            model.UserReward.user_id == user.id,
            model.UserReward.reward_id == reward_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Reward already claimed.")
    
    user_reward = model.UserReward(
        user_id=user.id,
        reward_id=reward_id
    )
    
    session.add(user_reward)
    session.commit()
    session.refresh(user_reward)
    return user_reward

def use_reward(user: User, user_reward_id: uuid.UUID, session: Session) -> model.UserReward:
    user_reward = session.exec(
        select(model.UserReward).where(
            model.UserReward.id == user_reward_id,
            model.UserReward.user_id == user.id
        )
    ).first()
    
    if not user_reward:
        raise HTTPException(status_code=404, detail="Reward not found or does not belong to user.")
    
    if user_reward.is_used:
        raise HTTPException(status_code=400, detail="Reward has already been used.")
    
    user_reward.is_used = True
    user_reward.used_at = datetime.now()
    
    session.commit()
    session.refresh(user_reward)
    return user_reward

def get_user_rewards(user: User, session: Session) -> list:
    user_rewards = session.exec(
        select(model.UserReward).where(model.UserReward.user_id == user.id)
    ).all()
    
    reward_ids = [ur.reward_id for ur in user_rewards]
    
    rewards = session.exec(
        select(model.Reward).where(model.Reward.id.in_(reward_ids))
    ).all()
    
    result = []
    for ur in user_rewards:
        reward = next((r for r in rewards if r.id == ur.reward_id), None)
        if reward:
            reward_dict = reward.dict()
            reward_dict['claimed_at'] = ur.claimed_at
            reward_dict['is_used'] = ur.is_used
            reward_dict['used_at'] = ur.used_at
            reward_dict['user_reward_id'] = ur.id
            result.append(reward_dict)
    
    return result

