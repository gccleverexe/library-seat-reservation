from passlib.context import CryptContext

from backend.database import Base, SessionLocal, engine
from backend.models import User, Seat  # noqa: F401 — registers all models with Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SEAT_DATA = [
    {"floor": 1, "area": "阅览区A", "prefix": "F1"},
    {"floor": 2, "area": "阅览区B", "prefix": "F2"},
    {"floor": 3, "area": "自习区",  "prefix": "F3"},
]


def init_db() -> None:
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Default admin account
        if not db.query(User).filter(User.campus_id == "admin").first():
            admin = User(
                campus_id="admin",
                name="图书馆管理员",
                hashed_password=pwd_context.hash("admin123"),
                role="admin",
            )
            db.add(admin)

        # Sample seats: 3 floors × 10 seats
        for floor_info in SEAT_DATA:
            for i in range(1, 11):
                seat_number = f"{floor_info['prefix']}-{i:02d}"
                if not db.query(Seat).filter(Seat.seat_number == seat_number).first():
                    seat = Seat(
                        seat_number=seat_number,
                        floor=floor_info["floor"],
                        area=floor_info["area"],
                        status="available",
                    )
                    db.add(seat)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
