from fastapi import FastAPI, Depends, status, HTTPException, Response, APIRouter
from .. database import  get_db
from typing import List 
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2


router = APIRouter(prefix='/posts', tags=['posts'])

@router.get('/', response_model = List[schemas.PostOut])
def get_post(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), offset: int =0, limit: int=10):

    posts = db.query(models.Post, func.count(models.Vote.post_id).label('vote')).join(models.Vote, models.Vote.post_id==models.Post.id, isouter=True).group_by(models.Post.id).limit(limit).offset(offset).all()
    # .limit(limit).all()

    return  posts



@router.get('/{id}', response_model=schemas.PostOut)
def get_single_post(id:int , db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    query_post = db.query(models.Post, func.count(models.Vote.post_id).label('vote')).join(models.Vote,  models.Vote.post_id==models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not query_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} not found")

    return query_post
 
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def post_create(post: schemas.PostBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    new_post = models.Post(owner_id = current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.put('/{id}', response_model=schemas.Post)
def post_update(id:int , updated_post: schemas.PostBase, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    query_post = db.query(models.Post).filter(models.Post.id==id)

    post = query_post.first()

    if post ==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to preform request action')
    
    query_post.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return query_post.first()

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def post_delete(id: int, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id==id)

    if post.first() ==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} not found")

    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to perform requested action')
    
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

