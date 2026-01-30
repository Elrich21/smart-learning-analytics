from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    degree: str | None = None
    academic_year: int | None = None


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    degree: str | None = None
    academic_year: int | None = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
