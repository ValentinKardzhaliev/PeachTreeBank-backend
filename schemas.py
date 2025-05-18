from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    from_account: str
    to_account: str
    amount: float
    status: Literal['red', 'yellow', 'green']

class TransactionCreate(TransactionBase):
    status: Literal['red', 'yellow', 'green'] = 'red'

class Transaction(TransactionBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True

class TransactionStatusUpdate(BaseModel):
    status: Literal['red', 'yellow', 'green']
