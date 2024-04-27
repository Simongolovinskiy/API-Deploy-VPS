from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .config import settings

from datetime import timedelta, datetime

from .schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_jwt_token(payload: dict):
    encoding = payload.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encoding.update({"exp": expire})
    token = jwt.encode(encoding, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_jwt_token(token: str, credentials_error):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username, password = payload.get("username"), payload.get("password")
        if not username or not password:
            raise credentials_error
        token_data = TokenData(username=username, password=password)
    except JWTError:
        raise credentials_error
    return token_data


def fetch_current_user(token_data: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    unauthorized_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate the credentials. Try again.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token = verify_jwt_token(token_data, unauthorized_error)
    user = db.query(User.id, User.email, User.created_at) \
        .filter(User.email == token.username) \
        .first()
    return user

