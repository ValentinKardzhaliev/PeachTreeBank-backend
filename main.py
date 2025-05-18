from fastapi import FastAPI, Depends, HTTPException, Response, Cookie, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from enum import Enum
import models, schemas
from database import engine, get_db, SessionLocal
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        yield
    finally:
        db.close()

app = FastAPI(lifespan=lifespan)
models.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:5173",
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

async def get_current_user(
    db: Session = Depends(get_db),
    session_id: str = Cookie(None, alias="session")
):
    if session_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = db.query(models.User).filter(models.User.id == int(session_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    return user

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if get_user(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = models.User(username=user.username)
    db_user.set_password(user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login/")
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, user.username)
    if not db_user or not db_user.check_password(user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    response = Response(content="{ \"message\": \"Login successful\" }", media_type="application/json")
    response.set_cookie(
        key="session",
        value=str(db_user.id),
        secure=True,
        samesite="lax",
    )
    return response

@app.post("/logout/")
def logout_user(response: Response):
    response.delete_cookie("session")
    return {"message": "Logout successful"}

class StatusEnum(str, Enum):
    red = "red"
    yellow = "yellow"
    green = "green"

@app.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_transaction = models.Transaction(**transaction.dict(), owner_id=current_user.id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions/", response_model=list[schemas.Transaction])
def list_transactions(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sort_by: str = Query("date", pattern="^(date|amount|contractor)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    contractor: str | None = Query(None),
    date: datetime | None = Query(None) 
):
    query = db.query(models.Transaction).filter(models.Transaction.owner_id == current_user.id)

    if contractor:
        query = query.filter(models.Transaction.to_account.ilike(f"%{contractor}%"))

    if date:
        start = datetime(date.year, date.month, date.day)
        end = start + timedelta(days=1)
        query = query.filter(models.Transaction.date >= start, models.Transaction.date < end)

    col_name = "to_account" if sort_by == "contractor" else sort_by
    col = getattr(models.Transaction, col_name)
    if order == "desc":
        col = col.desc()

    query = query.order_by(col)
    return query.offset(skip).limit(limit).all()


@app.get("/transactions/{transaction_id}", response_model=schemas.Transaction)
def read_transaction(
    transaction_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.id == transaction_id,
            models.Transaction.owner_id == current_user.id
        )
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@app.put("/transactions/{transaction_id}", response_model=schemas.Transaction)
def update_transaction_status(
    transaction_id: int,
    payload: schemas.TransactionStatusUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.id == transaction_id,
            models.Transaction.owner_id == current_user.id
        )
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    tx.status = payload.status
    db.commit()
    db.refresh(tx)
    return tx
