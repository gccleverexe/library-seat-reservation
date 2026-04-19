from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    campus_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")  # student / admin
    login_fail_count = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime, nullable=True)
    is_restricted = Column(Boolean, nullable=False, default=False)
    restricted_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
