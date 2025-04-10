# app/main.py (updated)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .auth import auth_router
from .views.user_view import router as user_router
from .views.game_view import router as game_router
from .views.challenge_view import router as challenge_router
from .views.participation_view import router as paticipation_router
from .views.achievement_view import router as achievement_router
from .views.level_view import router as level_router
from .views.reward_view import router as reward_router
from .views.gamification_view import router as gamification_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],  # Add both origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_start_up():
    init_db()
    # Initialize default levels and achievements
    setup_gamification()

@app.get("/")
def root():
    return {"message": "The server is running."}

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(game_router)
app.include_router(challenge_router)
app.include_router(paticipation_router)
app.include_router(achievement_router)
app.include_router(level_router)
app.include_router(reward_router)
app.include_router(gamification_router)


def setup_gamification():
    """
    Initialize default levels and achievements on first run
    """
    from sqlmodel import Session, select
    from .db import engine
    from .models.level_model import Level, LevelCreate
    from .models.achievement_model import Achievement, AchievementCreate, AchievementType
    from .models.reward_model import Reward, RewardCreate, RewardType
    from .models.user_model import User
    
    with Session(engine) as session:
        # Check if we already have levels
        levels = session.exec(select(Level)).all()
        if not levels:
            # Create default levels
            default_levels = [
                LevelCreate(number=1, name="Beginner", min_xp=0, max_xp=999, 
                           description="Just getting started"),
                LevelCreate(number=2, name="Novice", min_xp=1000, max_xp=2999, 
                           description="Learning the ropes"),
                LevelCreate(number=3, name="Apprentice", min_xp=3000, max_xp=7999, 
                           description="Making good progress"),
                LevelCreate(number=4, name="Journeyman", min_xp=8000, max_xp=14999, 
                           description="Becoming proficient"),
                LevelCreate(number=5, name="Expert", min_xp=15000, max_xp=24999, 
                           description="Mastering the challenges"),
                LevelCreate(number=6, name="Master", min_xp=25000, max_xp=39999, 
                           description="A true master of the craft"),
                LevelCreate(number=7, name="Grandmaster", min_xp=40000, max_xp=59999, 
                           description="Among the elite"),
                LevelCreate(number=8, name="Legend", min_xp=60000, max_xp=99999, 
                           description="Your name is known far and wide"),
                LevelCreate(number=9, name="Mythic", min_xp=100000, max_xp=149999, 
                           description="Stories are told of your accomplishments"),
                LevelCreate(number=10, name="Immortal", min_xp=150000, max_xp=1000000000, 
                           description="Your legacy will never be forgotten"),
            ]
            
            for level_data in default_levels:
                level = Level(**level_data.model_dump())
                session.add(level)
            
            session.commit()
            print("Default levels created")
        
        # Check if we already have achievements
        achievements = session.exec(select(Achievement)).all()
        if not achievements:
            # Create default achievements
            default_achievements = [
                # Challenge completion achievements
                AchievementCreate(
                    name="Challenge Accepted", 
                    description="Complete your first challenge",
                    type=AchievementType.CHALLENGE_COMPLETION,
                    threshold=1
                ),
                AchievementCreate(
                    name="Getting In The Groove", 
                    description="Complete 5 challenges",
                    type=AchievementType.CHALLENGE_COMPLETION,
                    threshold=5
                ),
                AchievementCreate(
                    name="Challenge Master", 
                    description="Complete 25 challenges",
                    type=AchievementType.CHALLENGE_COMPLETION,
                    threshold=25
                ),
                AchievementCreate(
                    name="Challenge Champion", 
                    description="Complete 100 challenges",
                    type=AchievementType.CHALLENGE_COMPLETION,
                    threshold=100
                ),
                
                # Point milestone achievements
                AchievementCreate(
                    name="Point Collector", 
                    description="Earn 1,000 total points",
                    type=AchievementType.POINT_MILESTONE,
                    threshold=1000
                ),
                AchievementCreate(
                    name="Point Hoarder", 
                    description="Earn 10,000 total points",
                    type=AchievementType.POINT_MILESTONE,
                    threshold=10000
                ),
                AchievementCreate(
                    name="Point Mogul", 
                    description="Earn 100,000 total points",
                    type=AchievementType.POINT_MILESTONE,
                    threshold=100000
                ),
                
                # Participation count achievements
                AchievementCreate(
                    name="Participant", 
                    description="Join 3 different challenges",
                    type=AchievementType.PARTICIPATION_COUNT,
                    threshold=3
                ),
                AchievementCreate(
                    name="Dedicated Participant", 
                    description="Join 15 different challenges",
                    type=AchievementType.PARTICIPATION_COUNT,
                    threshold=15
                ),
                AchievementCreate(
                    name="Challenge Enthusiast", 
                    description="Join 50 different challenges",
                    type=AchievementType.PARTICIPATION_COUNT,
                    threshold=50
                ),
                
                # Streak achievements
                AchievementCreate(
                    name="Consistent", 
                    description="Maintain a 3-day activity streak",
                    type=AchievementType.STREAK,
                    threshold=3
                ),
                AchievementCreate(
                    name="Dedicated", 
                    description="Maintain a 7-day activity streak",
                    type=AchievementType.STREAK,
                    threshold=7
                ),
                AchievementCreate(
                    name="Committed", 
                    description="Maintain a 30-day activity streak",
                    type=AchievementType.STREAK,
                    threshold=30
                ),
                AchievementCreate(
                    name="Unstoppable", 
                    description="Maintain a 100-day activity streak",
                    type=AchievementType.STREAK,
                    threshold=100
                ),
            ]
            
            for achievement_data in default_achievements:
                achievement = Achievement(**achievement_data.model_dump())
                session.add(achievement)
            
            session.commit()
            print("Default achievements created")
        
        # Check if we already have rewards
        rewards = session.exec(select(Reward)).all()
        if not rewards:
            # Create default rewards
            default_rewards = [
                RewardCreate(
                    name="Bronze Badge", 
                    description="A badge to show your dedication",
                    type=RewardType.BADGE,
                    required_points=1000
                ),
                RewardCreate(
                    name="Silver Badge", 
                    description="A badge to show your expertise",
                    type=RewardType.BADGE,
                    required_points=5000
                ),
                RewardCreate(
                    name="Gold Badge", 
                    description="A badge to show your mastery",
                    type=RewardType.BADGE,
                    required_points=20000
                ),
                RewardCreate(
                    name="Platinum Badge", 
                    description="A badge to show your legendary status",
                    type=RewardType.BADGE,
                    required_points=50000
                ),
                RewardCreate(
                    name="Custom Theme Access", 
                    description="Unlock custom themes for the application",
                    type=RewardType.FEATURE_UNLOCK,
                    required_points=10000
                ),
                RewardCreate(
                    name="Advanced Analytics", 
                    description="Unlock advanced analytics features",
                    type=RewardType.FEATURE_UNLOCK,
                    required_points=30000
                ),
            ]
            
            for reward_data in default_rewards:
                reward = Reward(**reward_data.model_dump())
                session.add(reward)
            
            session.commit()
            print("Default rewards created")
        
        # Create admin user if none exists
        admin = session.exec(select(User).where(User.is_admin == True)).first()
        if not admin:
            from .auth import get_password_hash
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin1234"),
                is_admin=True
            )
            session.add(admin_user)
            session.commit()
            print("Admin user created")