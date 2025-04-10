from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated
import uuid
from ..db import get_session
from ..auth import decode_token
from ..controllers import gamification_controller as controller
from fastapi import HTTPException


router = APIRouter(tags=["gamification"])

@router.get("/users/me/stats")
def get_my_stats(*,
                my_user: Annotated[dict, Depends(decode_token)],
                session: Session = Depends(get_session)):
    return controller.get_user_stats(my_user, session)

@router.get("/games/{game_name}/leaderboard")
def get_leaderboard(*,
                   game_name: str,
                   limit: int = 10,
                   session: Session = Depends(get_session)):
    return controller.get_leaderboard(game_name, session, limit)

@router.post("/games/{game_name}/challenges/{challenge_id}/participations/{participation_id}/check-completion")
def check_challenge_completion(*,
                              game_name: str,
                              challenge_id: uuid.UUID,
                              participation_id: uuid.UUID,
                              my_user: Annotated[dict, Depends(decode_token)],
                              session: Session = Depends(get_session)):
    return controller.calculate_challenge_completion(my_user, participation_id, session)

@router.post("/games/{game_name}/challenges/{challenge_id}/collaborative-progress")
def update_collaborative_challenge(*,
                                  game_name: str,
                                  challenge_id: uuid.UUID,
                                  points: int,
                                  my_user: Annotated[dict, Depends(decode_token)],
                                  session: Session = Depends(get_session)):
    # First, add points to user's participation
    from ..models.participation_model import ParticipationAddPoints
    from ..controllers import participation_controller as part_controller
    
    # Get user's participation for this challenge
    participations = part_controller.get_participations(game_name, challenge_id, my_user, session)
    if not participations:
        raise HTTPException(status_code=404, detail="You are not participating in this challenge")
    
    participation = participations[0]  # Assuming one participation per user per challenge
    
    # Add points to user's participation
    add_points_data = ParticipationAddPoints(points=points)
    part_controller.add_points(game_name, challenge_id, participation.id, add_points_data, my_user, session)
    
    # Also add points to collaborative challenge pool
    return controller.process_collaborative_challenge_progress(challenge_id, points, session)

@router.post("/users/me/xp")
def add_xp_to_user(*,
                  xp_points: int,
                  my_user: Annotated[dict, Depends(decode_token)],
                  session: Session = Depends(get_session)):
    """Admin-only endpoint to manually add XP to a user"""
    if not my_user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return controller.award_xp_points(my_user, xp_points, session)