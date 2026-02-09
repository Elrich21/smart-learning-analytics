from fastapi import FastAPI, Depends, HTTPException

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import func


security = HTTPBearer()

from sqlalchemy.orm import Session
from jose import JWTError, jwt

from .database import engine, Base, get_db
from . import models, schemas
from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)
from .schemas import LoginRequest, TokenResponse

security = HTTPBearer()

app = FastAPI(title="Smart Learning Analytics Platform")

# Create tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Backend is running successfully"}


@app.post("/register", response_model=schemas.UserResponse, tags=["Auth"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        degree=user.degree,
        academic_year=user.academic_year,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login", response_model=TokenResponse, tags=["Auth"])
def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@app.get("/me", response_model=schemas.UserResponse, tags=["Users"])
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.post("/study-sessions", response_model=schemas.StudySessionResponse, tags=["Analytics"])
def create_study_session(
    session: schemas.StudySessionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_session = models.StudySession(
        user_id=current_user.user_id,
        course_id=session.course_id,
        duration_minutes=session.duration_minutes,
        study_method=session.study_method,
        focus_score=session.focus_score,
        time_of_day=session.time_of_day,
        session_date=session.session_date,
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session

@app.get("/analytics/summary", response_model=schemas.AnalyticsSummary, tags=["Analytics"])
def analytics_summary(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total_minutes = (
        db.query(func.coalesce(func.sum(models.StudySession.duration_minutes), 0))
        .filter(models.StudySession.user_id == current_user.user_id)
        .scalar()
    )

    avg_focus = (
        db.query(func.avg(models.StudySession.focus_score))
        .filter(models.StudySession.user_id == current_user.user_id)
        .scalar()
    )

    active_days = (
        db.query(func.count(func.distinct(models.StudySession.session_date)))
        .filter(models.StudySession.user_id == current_user.user_id)
        .scalar()
    )

    return {
        "total_minutes": int(total_minutes),
        "average_focus": float(avg_focus) if avg_focus is not None else 0.0,
        "active_days": int(active_days),
    }


@app.get("/analytics/by-course", response_model=list[schemas.CourseAnalytics], tags=["Analytics"])
def analytics_by_course(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(
            models.StudySession.course_id,
            func.sum(models.StudySession.duration_minutes).label("total_minutes"),
            func.avg(models.StudySession.focus_score).label("average_focus"),
        )
        .filter(models.StudySession.user_id == current_user.user_id)
        .group_by(models.StudySession.course_id)
        .all()
    )

    return [
        {
            "course_id": r.course_id,
            "total_minutes": int(r.total_minutes),
            "average_focus": float(r.average_focus),
        }
        for r in rows
    ]

