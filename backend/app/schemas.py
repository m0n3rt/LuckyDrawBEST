from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ParticipantBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    phone: Optional[str] = Field(default=None, max_length=32)
    email: Optional[str] = Field(default=None, max_length=120)

class ParticipantCreate(ParticipantBase):
    pass

class Participant(ParticipantBase):
    id: int
    created_at: datetime
    active: bool
    class Config:
        from_attributes = True

class Ticket(BaseModel):
    id: int
    number: int
    participant_id: int
    issue_type: str
    active: bool
    class Config:
        from_attributes = True

class Winner(BaseModel):
    id: int
    ticket_id: int
    session_id: int
    announced_at: datetime
    notification_status: str
    number: int
    class Config:
        from_attributes = True

class DrawSession(BaseModel):
    id: int
    prize_level: str
    seed: str
    hash_chain: str
    count: int
    created_at: datetime
    class Config:
        from_attributes = True

class RegisterResponse(BaseModel):
    ticket_number: int
    participant_id: int

class ParticipantList(BaseModel):
    total: int
    participants: List[Participant]

class DrawRequest(BaseModel):
    prize_level: str = Field(min_length=1)
    count: int = Field(gt=0, le=50, default=1)

class DrawResponse(BaseModel):
    session: DrawSession
    winners: List[Winner]
    prev_chain: str | None = None

class WinnerPublic(BaseModel):
    id: int
    number: int
    prize_level: str
    announced_at: datetime
    session_seed: str
    class Config:
        from_attributes = True

class WinnerList(BaseModel):
    total: int
    winners: List[WinnerPublic]
