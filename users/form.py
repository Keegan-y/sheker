from typing import Optional
from pydantic import BaseModel


class Login(BaseModel):
    email: str
    password: Optional[str] = None


class Regist(BaseModel):
    name: str
    email: str
    password: str
    password_ensure: str
    email_code: str
    group: str


class ResetPassword(BaseModel):
    email: str


class UpdatePassword(BaseModel):
    password: str
    password_ensure: str
    token: str
