from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import HTTPException
from ..models.user_model import User
from ..models import achievement_model as model
import uuid

def create_achievement(new_achievement: model.AchievementCreate, admin: User, session: Session) -> model.Achievement:
    if not admin.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    achievement = model.Achievement(**new_achievement.model_dump())
    session.add(achievement)
    session.commit()
    session.refresh(achievement)
    return achievement

def get_achievement_by_id(id: uuid.UUID, session: Session) -> model.Achievement:
    achievement = session.exec(
        select(model.Achievement).where(model.Achievement.id == id)
    ).first()
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found.")
    return achievement

def get_all_achievements(session: Session) -> list[model.Achievement]:
    return session.exec(select(model.Achievement)).all()

def award_achievement_to_user(user: User, achievement_id: uuid.UUID, session: Session) -> model.UserAchievement:
    achievement = get_achievement_by_id(id=achievement_id, session=session)
    
    # Check if user already has this achievement
    existing = session.exec(
        select(model.UserAchievement).where(
            model.UserAchievement.user_id == user.id,
            model.UserAchievement.achievement_id == achievement_id
        )
    ).first()
    
    if existing:
        return existing
    
    user_achievement = model.UserAchievement(
        user_id=user.id,
        achievement_id=achievement_id
    )
    
    session.add(user_achievement)
    session.commit()
    session.refresh(user_achievement)
    return user_achievement

def get_user_achievements(user: User, session: Session) -> list:
    user_achievements = session.exec(
        select(model.UserAchievement).where(model.UserAchievement.user_id == user.id)
    ).all()
    
    achievement_ids = [ua.achievement_id for ua in user_achievements]
    
    achievements = session.exec(
        select(model.Achievement).where(model.Achievement.id.in_(achievement_ids))
    ).all()
    
    result = []
    for achievement in achievements:
        ua = next(ua for ua in user_achievements if ua.achievement_id == achievement.id)
        achievement_dict = achievement.dict()
        achievement_dict['earned_at'] = ua.earned_at
        result.append(achievement_dict)
    
    return result

def check_achievements(user: User, session: Session) -> list[model.UserAchievement]:
    """
    Check and award any achievements that the user qualifies for
    """
    # Get all achievements
    all_achievements = get_all_achievements(session)
    
    # Get user's current achievements
    user_achievement_records = session.exec(
        select(model.UserAchievement).where(model.UserAchievement.user_id == user.id)
    ).all()
    user_achievement_ids = [ua.achievement_id for ua in user_achievement_records]
    
    # Get user participation data
    from ..models.participation_model import Participation
    participations = session.exec(
        select(Participation).where(Participation.user_id == user.id)
    ).all()
    
    # Get challenge data for completed challenges
    from ..models.challenge_model import Challenge
    challenge_ids = [p.challenge_id for p in participations]
    challenges = session.exec(
        select(Challenge).where(Challenge.id.in_(challenge_ids))
    ).all()
    
    # Map challenges to participations
    completed_challenges = []
    for p in participations:
        for c in challenges:
            if p.challenge_id == c.id and p.total_points >= p.needed_points:
                completed_challenges.append(c)
    
    newly_awarded = []
    
    # Check each achievement
    for achievement in all_achievements:
        # Skip if user already has this achievement
        if achievement.id in user_achievement_ids:
            continue
            
        should_award = False
        
        if achievement.type == model.AchievementType.CHALLENGE_COMPLETION:
            # Award if user has completed enough challenges
            if len(completed_challenges) >= achievement.threshold:
                should_award = True
                
        elif achievement.type == model.AchievementType.POINT_MILESTONE:
            # Award if user has enough total points
            if user.total_points >= achievement.threshold:
                should_award = True
                
        elif achievement.type == model.AchievementType.PARTICIPATION_COUNT:
            # Award if user has participated in enough challenges
            if len(participations) >= achievement.threshold:
                should_award = True
                
        elif achievement.type == model.AchievementType.STREAK:
            # Award if user has maintained activity streak
            if user.streak_days >= achievement.threshold:
                should_award = True
        
        if should_award:
            user_achievement = award_achievement_to_user(user, achievement.id, session)
            newly_awarded.append(user_achievement)
    
    return newly_awarded

