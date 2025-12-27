# inventory_api/app/api/deps.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

# Пока просто проброс зависимости — можно расширить позже
def get_db_session(db: Session = Depends(get_db)) -> Session:
    return db