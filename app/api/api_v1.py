"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.routes import private, utils
from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.items.router import router as items_router
from app.modules.users.router import router as users_router

api_router = APIRouter()

# Feature modules
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(items_router)

# Legacy utility and private routes
api_router.include_router(utils.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)

