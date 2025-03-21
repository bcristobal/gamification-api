from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

class Dificulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Participation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID | None =Field(default=None, foreign_key="user.id")
    challenge_id: uuid.UUID | None =Field(default=None, foreign_key="challenge.id")
    game_id: uuid.UUID | None =Field(default=None, foreign_key="game.id")
    dificulty: Dificulty
    total_points: int = 0
    needed_points: int
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class ParticipationCreate(SQLModel):
    dificulty: Dificulty

class ParticipationAddPoints(SQLModel):
    points: int