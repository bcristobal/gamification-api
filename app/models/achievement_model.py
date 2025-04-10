from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

class AchievementType(str, Enum):
    CHALLENGE_COMPLETION = "challenge_completion"
    POINT_MILESTONE = "point_milestone"
    PARTICIPATION_COUNT = "participation_count"
    STREAK = "streak"
    SPECIAL = "special"

class Achievement(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: str
    icon_url: Optional[str] = None
    type: AchievementType
    threshold: int  # Points, count, or days required
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class UserAchievement(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    achievement_id: uuid.UUID = Field(foreign_key="achievement.id")
    earned_at: datetime = Field(default_factory=lambda: datetime.now())
    
class AchievementCreate(SQLModel):
    name: str
    description: str
    icon_url: Optional[str] = None
    type: AchievementType
    threshold: int

class AchievementUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    threshold: Optional[int] = None

