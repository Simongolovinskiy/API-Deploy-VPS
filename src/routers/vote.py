from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, database, oauth2, models

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.get("/", status_code=status.HTTP_201_CREATED)
def do_vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.fetch_current_user)):
    current_post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

    if not current_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id {vote.post_id} not found.")

    query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    )

    vote_value = query.first()
    if vote.direction:
        if vote_value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=f"user with id {current_user.id} has already voted on post with id {vote.post_id}")
        new_vote = schemas.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": f"Successfully voted on post with id {vote.post_id}"}
    else:
        if not vote_value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"The post with id {vote.post_id} not found."
            )
        query.delete(synchronize_session=False)
        db.commit()
        return {"message": f"Successfully deleted post with id {vote.post_id}"}
