from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config import ACCESS_TOKEN_EXPIRE_HOURS, ALGORITHM, SECRET_KEY
from backend.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def _truncate(password: str) -> str:
    """bcrypt 限制密码最长 72 字节，超出截断。"""
    return password.encode("utf-8")[:72].decode("utf-8", errors="ignore")


def register(db: Session, campus_id: str, password: str, name: str) -> User:
    if db.query(User).filter(User.campus_id == campus_id).first():
        raise HTTPException(status_code=400, detail="该校园号已被注册")

    hashed_password = pwd_context.hash(_truncate(password))
    user = User(
        campus_id=campus_id,
        name=name,
        hashed_password=hashed_password,
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, campus_id: str, password: str) -> str:
    user = db.query(User).filter(User.campus_id == campus_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="账号或密码错误")

    if user.locked_until is not None and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=401,
            detail=f"账号已锁定，请在 {user.locked_until} 后重试",
        )

    if not pwd_context.verify(_truncate(password), user.hashed_password):
        user.login_fail_count += 1
        if user.login_fail_count >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            user.login_fail_count = 0
        db.commit()
        raise HTTPException(status_code=401, detail="账号或密码错误")

    user.login_fail_count = 0
    user.locked_until = None
    db.commit()

    payload = {
        "sub": user.campus_id,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="无效或已过期的令牌")
