from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


# --------- Bank Schemas ---------

class DepositRequest(BaseModel):
    account_id: int
    amount: float


class WithdrawRequest(BaseModel):
    account_id: int
    amount: float


class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float