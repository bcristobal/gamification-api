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
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class UserCreate(SQLModel):
    email: str
    username: str
    password: str

# TODO: Create a response model

class UserUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None