
from fastapi import FastAPI

from src.api.rest.routes.auth_route import AuthRouter
from src.api.rest.routes.admin_route import AdminRouter

from src.api.middleware.cors import register_cors_middleware

app = FastAPI(title="TalentIQ Auth")


register_cors_middleware(app)

app.include_router(AuthRouter, prefix="/api/v1")
app.include_router(AdminRouter, prefix="/api/v1")

