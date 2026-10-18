from fastapi import FastAPI

from src.api.middleware.cors import register_cors_middleware
from src.api.middleware.error_handler import register_exception_handlers
from src.api.middleware.logging import register_logging_middleware
from src.api.middleware.metrics import register_metrics_middleware
from src.api.middleware.rate_limiting import register_rate_limit_middleware
from src.api.rest.routes.admin_route import AdminRouter
from src.api.rest.routes.auth_route import AuthRouter
from src.api.rest.routes.user_route import UserRouter
from src.config.settings import settings


def create_app() -> FastAPI:
    """Builds the auth API: middleware, error handlers and routers."""
    app = FastAPI(
        title=settings.app_name,
        description="Sign-in, tokens, invitations and user profiles.",
        version="0.1.0",
    )
    # Middleware added last runs first: request logging (sets the request id)
    # wraps metrics, which wraps the rate limiter, then CORS.
    register_cors_middleware(app)
    register_rate_limit_middleware(app)
    register_metrics_middleware(app)
    register_logging_middleware(app)
    register_exception_handlers(app)

    app.include_router(AuthRouter, prefix="/api/v1")
    app.include_router(AdminRouter, prefix="/api/v1")
    app.include_router(UserRouter, prefix="/api/v1")
    return app
