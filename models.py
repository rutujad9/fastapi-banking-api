from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    accounts = relationship("Account", back_populates="owner")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="accounts")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    txn_type = Column(String, nullable=False)   # deposit | withdraw | transfer
    from_account = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    to_account = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)