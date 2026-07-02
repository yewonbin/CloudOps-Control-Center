from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, tasks
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.db import Base, engine
from app.models.user import User
from app.schemas.user import UserOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Phase 1: create tables directly. Alembic migrations arrive in a later phase.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Wide-open CORS for local dev; tightened once the React frontend has an origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["ops"])
def health() -> dict[str, str]:
    """Liveness probe used by Docker/Nginx/monitoring."""
    return {"status": "ok"}


api = APIRouter(prefix=settings.API_V1_PREFIX)
api.include_router(auth.router)
api.include_router(tasks.router)


@api.get("/me", response_model=UserOut, tags=["auth"])
def read_me(user: User = Depends(get_current_user)) -> User:
    return user


app.include_router(api)
