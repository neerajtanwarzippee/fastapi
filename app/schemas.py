from pydantic import BaseModel, EmailStr
from typing import List

#
# class ItemBase(BaseModel):
#     title: str
#     description: str | None = None
#
#
# class ItemCreate(ItemBase):
#     pass
#
#
# class Item(ItemBase):
#     id: int
#     owner_id: int
#
#     class Config:
#         orm_mode = True


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str
    email: str
    password: str
    is_active: bool


class TransactionBase(BaseModel):
    id: int
    amount: int
    type: str


class TransactionCreate(BaseModel):
    amount: int
    type: str


class TransactionUpdate(BaseModel):
    amount: int


class WalletBase(BaseModel):
    id: int
    amount: int
    user_id: int
    transactions: list[TransactionBase] = []

    class Config:
        orm_mode = True


class WalletCreate(WalletBase):
    pass


class User(UserBase):
    id: int
    is_active: bool
    wallet: WalletBase

    class Config:
        orm_mode = True


class EmailSchema(BaseModel):
    email: List[EmailStr]
