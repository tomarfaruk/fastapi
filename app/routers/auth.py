from fastapi import FastAPI, Depends, status, HTTPException, Response, APIRouter
from .. database import  get_db
from typing import List 
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter(tags=['auth'])

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm=Depends(), db: Session= Depends(get_db)):
    user = db.query(models.User).filter(models.User.email==user_credentials.username).first()

    credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"})

    if not user:
        raise credential_exception
    
    if not utils.verify_password(user_credentials.password, user.password):
        raise credential_exception

    access_token = oauth2.create_access_token(data = { 'user_id': user.id })
    return {"access_token": access_token, "token_type": "bearer"}

    
