from fastapi.routing import APIRouter

from simple_transactions.auth.web.api.v1 import monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
