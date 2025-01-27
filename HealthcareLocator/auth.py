from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import models

# Security constants
SECRET_KEY = "your-secret-key-here"  # Should be stored in environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_patient(db: Session, email: str, password: str):
    patient = db.query(models.Patient).filter(models.Patient.email == email).first()
    if not patient:
        return False
    if not verify_password(password, patient.hashed_password):
        return False
    return patient

def create_patient(
    db: Session,
    email: str,
    username: str,
    password: str,
    full_name: str,
    date_of_birth: datetime,
    phone_number: str
):
    hashed_password = get_password_hash(password)
    db_patient = models.Patient(
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=full_name,
        date_of_birth=date_of_birth,
        phone_number=phone_number
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient
