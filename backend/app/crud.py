from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from . import schemas
import hashlib, time, random
from .config import settings

def create_participant_with_ticket(db: Session, data: schemas.ParticipantCreate) -> schemas.RegisterResponse:
    participant = models.Participant(name=data.name, phone=data.phone, email=data.email)
    db.add(participant)
    db.flush()  # get id
    # 分配号码：取当前最大 +1
    max_number = db.query(func.max(models.Ticket.number)).scalar()
    next_number = (max_number or 0) + 1
    ticket = models.Ticket(number=next_number, participant_id=participant.id, issue_type="auto")
    db.add(ticket)
    db.commit()
    db.refresh(participant)
    return schemas.RegisterResponse(ticket_number=next_number, participant_id=participant.id)

def list_participants(db: Session, skip: int = 0, limit: int = 50) -> schemas.ParticipantList:
    q = db.query(models.Participant).order_by(models.Participant.id.desc())
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return schemas.ParticipantList(total=total, participants=items)

def list_active_tickets(db: Session):
    return db.query(models.Ticket).filter(models.Ticket.active == True).all()

def perform_draw(db: Session, prize_level: str, count: int) -> schemas.DrawResponse:
    # 获取当前有效票
    tickets = list_active_tickets(db)
    if not tickets:
        raise ValueError("No tickets to draw")
    # 种子: 时间戳+票数量+最后一次hash
    prev_hash = db.query(models.DrawSession.hash_chain).order_by(models.DrawSession.id.desc()).limit(1).scalar() or ''
    seed_source = f"{time.time()}|{len(tickets)}|{prev_hash}|{settings.DRAW_HASH_SALT}"
    seed = hashlib.sha256(seed_source.encode()).hexdigest()[:16]
    chain = hashlib.sha256((seed + prev_hash).encode()).hexdigest()
    rng = random.Random(seed)
    # 抽取：基于种子确定顺序，避免重复
    pool = tickets.copy()
    rng.shuffle(pool)
    winners_tickets = pool[:count]
    session = models.DrawSession(prize_level=prize_level, seed=seed, hash_chain=chain, count=count)
    db.add(session)
    db.flush()
    winners = []
    for t in winners_tickets:
        w = models.Winner(session_id=session.id, ticket_id=t.id)
        db.add(w)
        winners.append(w)
    db.commit()
    for w in winners:
        db.refresh(w)
    db.refresh(session)
    # 构造响应模型
    winner_models = []
    for w in winners:
        ticket_number = db.query(models.Ticket.number).filter(models.Ticket.id == w.ticket_id).scalar()
        winner_models.append(schemas.Winner(id=w.id, ticket_id=w.ticket_id, session_id=w.session_id,
                                            announced_at=w.announced_at, notification_status=w.notification_status,
                                            number=ticket_number))
    return schemas.DrawResponse(session=session, winners=winner_models, prev_chain=prev_hash or None)

def list_winners(db: Session, skip: int = 0, limit: int = 100) -> schemas.WinnerList:
    q = db.query(models.Winner).order_by(models.Winner.id.desc())
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    public: list[schemas.WinnerPublic] = []
    for w in items:
        ticket_number = db.query(models.Ticket.number).filter(models.Ticket.id == w.ticket_id).scalar()
        session = db.query(models.DrawSession).filter(models.DrawSession.id == w.session_id).first()
        if session is None:
            continue
        public.append(schemas.WinnerPublic(id=w.id, number=ticket_number, prize_level=session.prize_level,
                                           announced_at=w.announced_at, session_seed=session.seed))
    return schemas.WinnerList(total=total, winners=public)
