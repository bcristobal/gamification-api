from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated

from ..db import get_session
from ..models import user_model as model
from ..controllers import user_controller as controller
from ..auth import decode_token


router = APIRouter(prefix="/users", tags=["user"])


@router.post("/")
def create_user(*,new_user: model.UserCreate, session: Session = Depends(get_session)):
    is_created = controller.create_user(new_user=new_user, session=session)
    if is_created: 
        return {"message": "User was correctly created."}
    

@router.get("/me")
def get_my_user(*, my_user: Annotated[dict, Depends(decode_token)]):
    return my_user


@router.put("/me")
def update_my_user(*,
                   updated_user: model.UserUpdate,
                   my_user: Annotated[dict, Depends(decode_token)],
                   session: Session = Depends(get_session)):
    return controller.update_user(updated_user=updated_user, user=my_user, session=session)


@router.delete("/me")
def delete_my_user(*,
                   my_user: Annotated[dict, Depends(decode_token)],
                   session: Session = Depends(get_session)):
    return controller.delete_user(user=my_user, session=session)