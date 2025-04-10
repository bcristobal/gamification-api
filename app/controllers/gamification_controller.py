from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import HTTPException
from ..models.user_model import User
from ..models.participation_model import Participation
from ..models.challenge_model import Challenge
from ..controllers.achievement_controller import check_achievements
from ..controllers.level_controller import update_user_level
import uuid

def award_xp_points(user: User, points: int, session: Session) -> User:
    """
    Award experience points to a user and update their level
    """
    user.xp_points += points
    user.total_points += points
    
    # Update last activity and maintain streak
    now = datetime.now()
    if user.last_activity:
        # If last activity was more than 1 day ago but less than 2 days ago
        # (meaning user was active yesterday)
        time_diff = now - user.last_activity
        if timedelta(days=1) <= time_diff < timedelta(days=2):
            user.streak_days += 1
        elif time_diff >= timedelta(days=2):
            # Reset streak if more than 2 days
            user.streak_days = 1
    else:
        # First activity
        user.streak_days = 1
    
    user.last_activity = now
    
    session.commit()
    
    # Update user's level based on XP
    user = update_user_level(user, session)
    
    # Check for new achievements
    check_achievements(user, session)
    
    return user

def calculate_challenge_completion(user: User, participation_id: uuid.UUID, session: Session) -> dict:
    """
    Calculate and process challenge completion rewards
    """
    participation = session.exec(
        select(Participation).where(
            Participation.id == participation_id,
            Participation.user_id == user.id
        )
    ).first()
    
    if not participation:
        raise HTTPException(status_code=404, detail="Participation not found.")
    
    challenge = session.exec(
        select(Challenge).where(Challenge.id == participation.challenge_id)
    ).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")
    
    # Calculate completion percentage
    completion_percent = min(100, (participation.total_points / participation.needed_points * 100))
    is_completed = completion_percent >= 100
    
    # Award XP based on progress
    xp_earned = 0
    if is_completed:
        # Bonus XP for completion
        difficulty_multiplier = 1
        if participation.dificulty == "medium":
            difficulty_multiplier = 2
        elif participation.dificulty == "hard":
            difficulty_multiplier = 3
            
        xp_earned = challenge.points * difficulty_multiplier
        user = award_xp_points(user, xp_earned, session)
    
    return {
        "participation_id": participation.id,
        "challenge_id": challenge.id,
        "completion_percentage": completion_percent,
        "is_completed": is_completed,
        "xp_earned": xp_earned,
        "current_xp": user.xp_points
    }

def get_leaderboard(game_name: str, session: Session, limit: int = 10) -> list:
    """
    Get leaderboard for a specific game
    """
    from ..controllers.game_controller import get_game_by_name
    
    game = get_game_by_name(name=game_name, session=session)
    
    # Get all participations for this game
    participations = session.exec(
        select(Participation).where(Participation.game_id == game.id)
    ).all()
    
    # Group by user and sum points
    user_points = {}
    for p in participations:
        if p.user_id not in user_points:
            user_points[p.user_id] = 0
        user_points[p.user_id] += p.total_points
    
    # Sort users by points
    sorted_users = sorted(user_points.items(), key=lambda x: x[1], reverse=True)
    
    # Get top users
    top_user_ids = [user_id for user_id, _ in sorted_users[:limit]]
    
    # Get user details
    users = session.exec(
        select(User).where(User.id.in_(top_user_ids))
    ).all()
    
    # Build leaderboard
    leaderboard = []
    for index, (user_id, points) in enumerate(sorted_users[:limit]):
        user = next((u for u in users if u.id == user_id), None)
        if user:
            leaderboard.append({
                "rank": index + 1,
                "username": user.username,
                "points": points
            })
    
    return leaderboard

def process_collaborative_challenge_progress(challenge_id: uuid.UUID, points_to_add: int, session: Session) -> dict:
    """
    Process progress for collaborative challenges - adds points to the challenge's community total
    """
    challenge = session.exec(
        select(Challenge).where(Challenge.id == challenge_id)
    ).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")
    
    if challenge.type != "collaborative":
        raise HTTPException(status_code=400, detail="Challenge is not collaborative.")
    
    # Add points to the collaborative pool
    challenge.all_users_points += points_to_add
    
    session.commit()
    session.refresh(challenge)
    
    # Calculate completion percentage
    completion_percent = min(100, (challenge.all_users_points / challenge.points * 100))
    is_completed = completion_percent >= 100
    
    return {
        "challenge_id": challenge.id,
        "current_points": challenge.all_users_points,
        "target_points": challenge.points,
        "completion_percentage": completion_percent,
        "is_completed": is_completed
    }

def get_user_stats(user: User, session: Session) -> dict:
    """
    Get comprehensive stats for a user
    """
    # Get user participations
    participations = session.exec(
        select(Participation).where(Participation.user_id == user.id)
    ).all()
    
    # Get challenges
    challenge_ids = [p.challenge_id for p in participations]
    challenges = session.exec(
        select(Challenge).where(Challenge.id.in_(challenge_ids))
    ).all()
    
    # Calculate stats
    total_challenges = len(challenge_ids)
    completed_challenges = sum(1 for p in participations if p.total_points >= p.needed_points)
    
    # Calculate completion rate
    completion_rate = 0
    if total_challenges > 0:
        completion_rate = (completed_challenges / total_challenges) * 100
    
    # Get current level
    from ..models.level_model import Level
    current_level = None
    if user.level_id:
        current_level = session.exec(
            select(Level).where(Level.id == user.level_id)
        ).first()
    
    # Calculate XP needed for next level
    xp_for_next_level = None
    if current_level:
        next_level = session.exec(
            select(Level).where(Level.number == current_level.number + 1)
        ).first()
        if next_level:
            xp_for_next_level = next_level.min_xp - user.xp_points
    
    return {
        "username": user.username,
        "total_xp": user.xp_points,
        "total_points": user.total_points,
        "streak_days": user.streak_days,
        "current_level": current_level.number if current_level else None,
        "level_name": current_level.name if current_level else None,
        "xp_for_next_level": xp_for_next_level,
        "total_challenges": total_challenges,
        "completed_challenges": completed_challenges,
        "completion_rate": completion_rate,
        "last_activity": user.last_activity
    }
