from fastapi.routing import APIRouter

from simple_transactions.auth.web.api.v1 import monitoring
from simple_transactions.auth.web.api.v1 import auth

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(auth.router, prefix="/api/v1/auth")
