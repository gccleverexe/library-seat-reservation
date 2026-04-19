from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from backend.init_db import init_db
from backend.services.scheduler import auto_release_expired_reservations

app = FastAPI(title="校园图书馆座位预约系统", version="1.0.0")

# ---------------------------------------------------------------------------
# CORS — allow all origins for development
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Module-level scheduler so it can be accessed in the shutdown event
scheduler = BackgroundScheduler()

# ---------------------------------------------------------------------------
# Startup event — initialise database tables and start scheduler
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event() -> None:
    init_db()
    scheduler.add_job(auto_release_expired_reservations, "interval", seconds=60)
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    scheduler.shutdown(wait=False)


# ---------------------------------------------------------------------------
# Routers — uncomment as each router module is implemented
# ---------------------------------------------------------------------------
from backend.routers import auth
app.include_router(auth.router,         prefix="/api/auth",               tags=["auth"])
from backend.routers import seats
app.include_router(seats.router,        prefix="/api/seats",              tags=["seats"])
from backend.routers import reservations
app.include_router(reservations.router, prefix="/api/reservations",       tags=["reservations"])
from backend.routers import checkin
app.include_router(checkin.router,      prefix="/api",                    tags=["checkin"])
from backend.routers import admin
app.include_router(admin.router,        prefix="/api/admin",              tags=["admin"])
