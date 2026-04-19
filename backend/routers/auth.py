from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user, success_response
from backend.schemas.auth import RegisterRequest, LoginRequest, UserInfo
from backend.services import auth_service
from backend.models.user import User

router = APIRouter()


@router.post("/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register(db, body.campus_id, body.password, body.name)
    return success_response(UserInfo.model_validate(user), "注册成功", 201)


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    token = auth_service.login(db, body.campus_id, body.password)
    return success_response({"access_token": token, "token_type": "bearer"}, "登录成功")


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return success_response(UserInfo.model_validate(current_user))
