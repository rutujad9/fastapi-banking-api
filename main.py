from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import engine, Base, SessionLocal
import models
from schemas import UserCreate, UserResponse, DepositRequest, WithdrawRequest, TransferRequest
app = FastAPI()
DEBUG = False

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def log_txn(
    db: Session,
    txn_type: str,
    amount: float,
    from_acc: Optional[int] = None,
    to_acc: Optional[int] = None,
):
    db.add(
        models.Transaction(
            txn_type=txn_type,
            amount=amount,
            from_account=from_acc,
            to_account=to_acc,
        )
    )


@app.get("/")
def health_check():
    return {"message": "Tiny Bank API is running"}


@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.add(models.Account(owner_id=new_user.id))
    db.commit()

    return new_user


@app.post("/deposit")
def deposit(data: DepositRequest, db: Session = Depends(get_db)):
    account = (
        db.query(models.Account)
        .filter(models.Account.id == data.account_id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    account.balance += data.amount
    log_txn(db, "deposit", data.amount, to_acc=account.id)

    db.commit()
    return {"message": "Deposit successful", "balance": account.balance}


@app.post("/withdraw")
def withdraw(data: WithdrawRequest, db: Session = Depends(get_db)):
    account = (
        db.query(models.Account)
        .filter(models.Account.id == data.account_id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if account.balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    account.balance -= data.amount
    log_txn(db, "withdraw", data.amount, from_acc=account.id)

    db.commit()
    return {"message": "Withdraw successful", "balance": account.balance}


@app.post("/transfer")
def transfer(data: TransferRequest, db: Session = Depends(get_db)):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if data.from_account_id == data.to_account_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")

    sender = (
        db.query(models.Account)
        .filter(models.Account.id == data.from_account_id)
        .first()
    )
    receiver = (
        db.query(models.Account)
        .filter(models.Account.id == data.to_account_id)
        .first()
    )

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Account not found")
    if sender.balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    sender.balance -= data.amount
    receiver.balance += data.amount

    log_txn(db, "transfer", data.amount, from_acc=sender.id, to_acc=receiver.id)

    db.commit()
    return {
        "message": "Transfer successful",
        "from_balance": sender.balance,
        "to_balance": receiver.balance,
    }


@app.get("/transactions/{account_id}")
def transactions(account_id: int, db: Session = Depends(get_db)):
    txns = (
        db.query(models.Transaction)
        .filter(
            (models.Transaction.from_account == account_id)
            | (models.Transaction.to_account == account_id)
        )
        .order_by(models.Transaction.created_at.desc())
        .all()
    )
    return txns


@app.get("/users", include_in_schema=False)
def get_users(db: Session = Depends(get_db)):
    if not DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    return db.query(models.User).all()


@app.get("/accounts", include_in_schema=False)
def get_accounts(db: Session = Depends(get_db)):
    if not DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    return db.query(models.Account).all()