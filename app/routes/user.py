from fastapi import Response, HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
# from .. import database, schemas, models, utils
# from ..schemas import UserCreate
from database import get_db
from schemas import UserCreate
from utils import hash
from models import User





router = APIRouter(
    tags=['User']
)


@router.post('/signup',status_code=status.HTTP_201_CREATED)
def createUser(user:UserCreate, db:Session=Depends(get_db)):

    user.password = hash(user.password)

    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


