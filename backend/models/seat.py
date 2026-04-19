from sqlalchemy import Column, DateTime, Integer, String, func

from backend.database import Base


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    seat_number = Column(String, unique=True, nullable=False, index=True)
    floor = Column(Integer, nullable=False)
    area = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="available")  # available/reserved/occupied/unavailable
    created_at = Column(DateTime, nullable=False, default=func.now())
