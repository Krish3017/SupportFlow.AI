from pydantic import BaseModel, EmailStr

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminAuthResponse(BaseModel):
    token: str
    username: str
