from fastapi import APIRouter

from app.api.routes.auth import check, login, token
from app.api.routes.auth.sse import sse

sub_router = APIRouter(prefix="/auth", tags=["Auth"])

sub_router.include_router(login.router)
sub_router.include_router(check.router)
sub_router.include_router(token.router)
sub_router.include_router(sse.router)
