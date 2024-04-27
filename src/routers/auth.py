from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from typing import Annotated
from sqlalchemy.orm import Session

from ..database import get_db
from ..oauth2 import create_jwt_token
from ..schemas import Token
from ..models import User
from ..utils import verify_password

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    current_user = db.query(User).filter(User.email == credentials.username).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect credentials. Try again."
        )
    if not verify_password(credentials.password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The current password is not valid.")
    token = create_jwt_token(payload=dict(username=credentials.username,password=credentials.password))
    return {"access_token": token, "token_type": "Bearer"}


# 11:14:35
