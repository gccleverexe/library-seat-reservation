from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, func

from backend.database import Base


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=True)
    type = Column(String, nullable=False)  # no_checkin
    note = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    __table_args__ = (
        Index("ix_violations_user_id", "user_id"),
    )


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=True)
    target_id = Column(Integer, nullable=True)
    detail = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
