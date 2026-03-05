from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
import models
from schemas import UserCreate, UserResponse, RegisterResponse, DepositRequest, WithdrawRequest, TransferRequest, TokenResponse
from auth import hash_password, verify_password, create_access_token, decode_token

app = FastAPI()
DEBUG = False

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")


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
    return {"status": "ok", "service": "FastAPI Banking API"}


@app.post("/register", response_model=RegisterResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    account = models.Account(owner_id=new_user.id)
    db.add(account)
    db.commit()
    db.refresh(account)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "account_id": account.id
    }


@app.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 form uses "username" field -> we treat it as email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/deposit")
def deposit(
    data: DepositRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    account = db.query(models.Account).filter(models.Account.id == data.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    account.balance += data.amount
    log_txn(db, "deposit", data.amount, to_acc=account.id)
    db.commit()

    return {"message": "Deposit successful", "balance": account.balance}


@app.post("/withdraw")
def withdraw(
    data: WithdrawRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    account = db.query(models.Account).filter(models.Account.id == data.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    if account.balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    account.balance -= data.amount
    log_txn(db, "withdraw", data.amount, from_acc=account.id)
    db.commit()

    return {"message": "Withdraw successful", "balance": account.balance}


@app.post("/transfer")
def transfer(
    data: TransferRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if data.from_account_id == data.to_account_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")

    sender = db.query(models.Account).filter(models.Account.id == data.from_account_id).first()
    receiver = db.query(models.Account).filter(models.Account.id == data.to_account_id).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Account not found")
    if sender.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
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
def transactions(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

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