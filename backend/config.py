import os

# Database
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./library.db")

# JWT
SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS: int = 24
