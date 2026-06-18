from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Database imports
from app.database import engine, get_db, Base
import app.models as models

# Existing imports
from app.schemas import UserOut, UserAuth, TokenSchema
from app.utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password
)

# Automatically generate SQLite database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.post('/signup', summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth, db: Session = Depends(get_db)):
    # Query database to check if user already exists
    user_exists = db.query(models.User).filter(models.User.email == data.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Create new database record instance
    new_user = models.User(
        id=str(uuid4()),
        username=data.username,
        email=data.email,
        password=get_hashed_password(data.password)
    )

    # Commit changes to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm passes the email string through the .username field
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found!"
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }

@app.get("/users", response_model=list[UserOut])
async def get_users(db: Session = Depends(get_db)):
    # Query all users from the SQL table
    return db.query(models.User).all()
