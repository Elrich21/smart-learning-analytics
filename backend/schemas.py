from pydantic import BaseModel, EmailStr
from datetime import date


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

class StudySessionCreate(BaseModel):
    course_id: int
    duration_minutes: int
    study_method: str
    focus_score: int
    time_of_day: str
    session_date: date

class StudySessionResponse(BaseModel):
    session_id: int
    course_id: int
    duration_minutes: int
    study_method: str
    focus_score: int
    time_of_day: str
    session_date: date

    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    total_minutes: int
    average_focus: float
    active_days: int


class CourseAnalytics(BaseModel):
    course_id: int
    total_minutes: int
    average_focus: float

