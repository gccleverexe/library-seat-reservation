from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session

from backend.config import SECRET_KEY, ALGORITHM
from backend.database import get_db
from backend.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ---------------------------------------------------------------------------
# Unified response helpers
# ---------------------------------------------------------------------------

def success_response(data=None, message: str = "success", code: int = 200) -> dict:
    return {"code": code, "message": message, "data": data}


def error_response(message: str, code: int = 400, data=None) -> dict:
    return {"code": code, "message": message, "data": data}


# ---------------------------------------------------------------------------
# Dependency: get current authenticated user
# ---------------------------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        campus_id: str = payload.get("sub")
        if campus_id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证凭据已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.campus_id == campus_id).first()
    if user is None:
        raise credentials_exception
    return user


# ---------------------------------------------------------------------------
# Dependency: require admin role
# ---------------------------------------------------------------------------

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限执行此操作",
        )
    return current_user
