from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db, Base, engine
from .. import crud, schemas, models
from .websocket import broadcast

router = APIRouter(prefix="/api", tags=["participants"])

@router.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@router.post("/register", response_model=schemas.RegisterResponse)
async def register(data: schemas.ParticipantCreate, db: Session = Depends(get_db)):
    resp = crud.create_participant_with_ticket(db, data)
    # 广播注册事件 (不含隐私电话/邮箱)
    await broadcast({"event": "register", "payload": {"participant_id": resp.participant_id, "ticket_number": resp.ticket_number}})
    return resp

@router.get("/participants", response_model=schemas.ParticipantList)
def participants(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.list_participants(db, skip=skip, limit=limit)

@router.delete("/participants/clear")
def clear_participants(admin_token: str = Query("", description="管理员令牌"), db: Session = Depends(get_db)):
    from ..config import settings
    if admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")
    # 删除顺序: winners -> sessions -> tickets -> participants
    db.query(models.Winner).delete()
    db.query(models.DrawSession).delete()
    db.query(models.Ticket).delete()
    db.query(models.Participant).delete()
    db.commit()
    return {"status": "cleared"}
