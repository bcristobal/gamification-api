# app/models/user_model.py (updated)
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True)
    username: str = Field(unique=True)
    hashed_password: str
    is_admin: bool = False
    xp_points: int = 0
    total_points: int = 0
    streak_days: int = 0
    last_activity: Optional[datetime] = None
    level_id: Optional[uuid.UUID] = Field(default=None, foreign_key="level.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class UserCreate(SQLModel):
    email: str
    username: str
    password: str

class UserResponse(SQLModel):
    id: uuid.UUID
    email: str
    username: str
    is_admin: bool
    xp_points: int
    total_points: int
    streak_days: int
    last_activity: Optional[datetime] = None
    created_at: datetime

class UserUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None