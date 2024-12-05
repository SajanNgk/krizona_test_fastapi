from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future import select


SECRET_KEY = "sajan"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = "mysql://root@127.0.0.1:3306/krizona"


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")   


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)  
    email = Column(String(255), unique=True)  
    hashed_password = Column(String(255))  



engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


app = FastAPI()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if a plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models for FastAPI
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserInDB(UserCreate):
    id: int
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str


@app.get("/health", summary="Check Database Connection")
async def health_check(db: Session = Depends(get_db)):
    """Check if the database connection is valid."""
    try:
       
        db.query(User).first() 
        return {"status": "ok", "message": "Database connection is healthy."}
    except Exception as e:
       
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/signup", summary="User Signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully"}


@app.post("/login", response_model=Token, summary="User Login")
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user by email and return a JWT token."""
   
    db_user = db.query(User).filter(User.email == login_request.email).first()  # Use email instead of username
    if not db_user or not verify_password(login_request.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create the JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/", summary="Welcome")
async def root():
    """Welcome route."""
    return {"message": "Welcome to Krizona!"}