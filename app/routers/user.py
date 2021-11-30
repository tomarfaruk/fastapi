from fastapi import FastAPI, Depends, status,HTTPException,Response, APIRouter
import psycopg2
from psycopg2.extras import RealDictCursor
from ..database import engine, get_db
from typing import List 
from sqlalchemy.orm import Session
from .. import models, schemas, utils


router = APIRouter(prefix='/usrs',tags=['users'])
# user part
@router.get('/', response_model=List[schemas.User] )
def get_users(db: Session=Depends(get_db)):
    users = db.query(models.User).all()
    return users
 
@router.get('/{id}', response_model=schemas.User)
def get_signle_user(id: int, db: Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.id==id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with {id} dose not exist')
    return user

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.User )
def user_create(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hase_password = utils.get_password_hash(user.password)
    user.password = hase_password
    new_user = models.User(**user.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user