from typing import List, Optional

from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..oauth2 import fetch_current_user
from ..models import Post, Vote

from ..database import get_db
from src.schemas import PostOutput, PostCreate


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


@router.get("/", response_model=List[PostOutput])
async def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(fetch_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""):
    posts = db.query(Post, func.count(Vote.post_id).label("votes")).join(
        Vote, Vote.post_id == Post.id, isouter=True).group_by(Post.id).filter(
        Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


@router.post("/", response_model=PostOutput)
async def create_post(params: PostCreate, db: Session = Depends(get_db), current_user: int = Depends(fetch_current_user)):
    new_post = Post(owner_id=current_user.id, **params.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=PostOutput)
def get_post_by_id(id: int, db: Session = Depends(get_db)):
    post = db.query(Post, func.count(Vote.post_id).label("votes")).join(
        Vote, Vote.post_id == Post.id, isouter=True).group_by(Post.id).filter(
        Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(fetch_current_user)):
    session_query = db.query(Post).filter(Post.id == id)
    response = session_query.first()
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id= } does not exist")

    session_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
