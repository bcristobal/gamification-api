from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class Level(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    number: int
    name: str
    description: Optional[str] = None
    min_xp: int
    max_xp: int
    icon_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class LevelCreate(SQLModel):
    number: int
    name: str
    description: Optional[str] = None
    min_xp: int
    max_xp: int
    icon_url: Optional[str] = None

class LevelUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    min_xp: Optional[int] = None
    max_xp: Optional[int] = None
    icon_url: Optional[str] = None

