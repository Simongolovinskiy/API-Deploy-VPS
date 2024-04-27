from typing import List

from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..oauth2 import fetch_current_user
from ..database import get_db
from ..schemas import UserOutput, UserCreate
from ..models import User
from ..utils import hash_password


router = APIRouter(
    prefix="/users",
    tags=['Users'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOutput)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Username already exists.")
    user.password = hash_password(user.password)
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", status_code=status.HTTP_202_ACCEPTED, response_model=List[UserOutput])
def get_users(db: Session = Depends(get_db)):
    response = db.query(User).all()
    return response


@router.get("/{id}", response_model=UserOutput)
def get_user(id: int, current_user: int = Depends(fetch_current_user), db: Session = Depends(get_db)):
    print(id)
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with {id = } not found.")
    print(user)
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def get_user(id: int, db: Session = Depends(get_db)):
    user_query = db.query(User).filter(User.id == id)
    user = user_query.first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with {id = } not found.")
    user_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
