from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class DepositRequest(BaseModel):
    account_id: int
    amount: float = Field(gt=0, description="Deposit amount must be greater than 0")


class WithdrawRequest(BaseModel):
    account_id: int
    amount: float = Field(gt=0, description="Withdraw amount must be greater than 0")


class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float = Field(gt=0, description="Transfer amount must be greater than 0")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    account_id: int