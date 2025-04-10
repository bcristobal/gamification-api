from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

class RewardType(str, Enum):
    BADGE = "badge"
    DISCOUNT = "discount"
    FEATURE_UNLOCK = "feature_unlock"
    VIRTUAL_ITEM = "virtual_item"
    REAL_ITEM = "real_item"

class Reward(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: str
    type: RewardType
    value: Optional[str] = None  # For discount codes or special values
    icon_url: Optional[str] = None
    required_points: int
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class UserReward(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    reward_id: uuid.UUID = Field(foreign_key="reward.id")
    claimed_at: datetime = Field(default_factory=lambda: datetime.now())
    is_used: bool = False
    used_at: Optional[datetime] = None

class RewardCreate(SQLModel):
    name: str
    description: str
    type: RewardType
    value: Optional[str] = None
    icon_url: Optional[str] = None
    required_points: int

class RewardUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    value: Optional[str] = None
    icon_url: Optional[str] = None
    required_points: Optional[int] = None

