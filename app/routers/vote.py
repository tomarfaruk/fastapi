from fastapi import FastAPI, Depends, status,HTTPException,Response, APIRouter
import psycopg2
from psycopg2.extras import RealDictCursor
from ..database import engine, get_db
from typing import List 
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2

router = APIRouter(prefix='/votes',tags=['vote'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user)):
    print(vote)

    find_post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

    vote_post = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)

    if not find_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    
    if vote.dir == 1:
        if vote_post.first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user has already voted")
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return {'message' : "Successfully added vote"}
    else:
        if not vote_post.first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='vote dose not exist')
        vote_post.delete(synchronize_session=False)
        db.commit()

        return {'message' : 'sussessfully deleted vote'}

    
    return {'sfdjgfd':'sjgf'}

