from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from simple_transactions.operation.web.api.v1.router import api_router
from simple_transactions.operation.web.lifespan import lifespan_setup


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="simple_transactions_operation",
        version=metadata.version("simple_transactions"),
        lifespan=lifespan_setup,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="")

    return app
