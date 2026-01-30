from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

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
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")

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
