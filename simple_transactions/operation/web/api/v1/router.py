from fastapi.routing import APIRouter

from simple_transactions.operation.web.api.v1 import monitoring, operation

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(operation.router, prefix="/api/v1/operation")
