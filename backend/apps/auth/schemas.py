from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthUserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    company_customer_id: Optional[str] = None


class AuthTokenResponse(BaseModel):
    token: str
    user: AuthUserResponse
