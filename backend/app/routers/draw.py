from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas
from .websocket import broadcast

router = APIRouter(prefix="/api", tags=["draw"])

@router.post("/draw", response_model=schemas.DrawResponse)
async def draw(req: schemas.DrawRequest, db: Session = Depends(get_db)):
    try:
        result = crud.perform_draw(db, prize_level=req.prize_level, count=req.count)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # 广播抽奖事件
    await broadcast({"event": "draw", "payload": result.dict()})
    return result

@router.get("/winners", response_model=schemas.WinnerList)
def winners(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_winners(db, skip=skip, limit=limit)
