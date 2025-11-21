from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), nullable=False)
    phone = Column(String(32), nullable=True, index=True)
    email = Column(String(120), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    active = Column(Boolean, default=True)
    tickets = relationship("Ticket", back_populates="participant")

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, index=True, nullable=False)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    issue_type = Column(String(16), default="auto")  # auto|manual|reserved
    active = Column(Boolean, default=True)
    participant = relationship("Participant", back_populates="tickets")
    winners = relationship("Winner", back_populates="ticket")

class DrawSession(Base):
    __tablename__ = "draw_sessions"
    id = Column(Integer, primary_key=True, index=True)
    prize_level = Column(String(40), nullable=False)
    seed = Column(String(64), nullable=False)
    hash_chain = Column(String(128), nullable=False)
    count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    winners = relationship("Winner", back_populates="session")

class Winner(Base):
    __tablename__ = "winners"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("draw_sessions.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    announced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notification_status = Column(String(16), default="pending")  # pending|sent|failed
    session = relationship("DrawSession", back_populates="winners")
    ticket = relationship("Ticket", back_populates="winners")
    __table_args__ = (UniqueConstraint("session_id", "ticket_id", name="uq_session_ticket"),)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    action_type = Column(String(32), nullable=False)
    payload = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
