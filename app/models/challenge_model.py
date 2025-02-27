from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ChallengeType(str, Enum):
    INDIVIDUAL = "individual"
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"

class Challenge(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: str
    start_date: datetime 
    finish_date: datetime
    points: int
    all_users_points: int = 0
    type: ChallengeType
    game_id: uuid.UUID | None = Field(default=None, foreign_key="game.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class ChallengeCreate(SQLModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    finish_date: datetime
    points: int
    type: ChallengeType

class ChallengeUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    points: Optional[int] = None
    type: Optional[ChallengeType] = None