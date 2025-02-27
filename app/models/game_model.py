from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class Game(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True)
    description: str
    strategy: str
    creator_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class GameCreate(SQLModel):
    
    name: str
    description: str
    strategy: str

class GameUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    strategy: Optional[str] = None