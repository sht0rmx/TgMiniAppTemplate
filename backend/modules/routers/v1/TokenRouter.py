from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from decouple import config
import jwt
from sqlalchemy import select
from dependencies.auth import jwt_required
from modules.db.engine import Database
from modules.db.models.RefreshToken import RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession
from modules.services.TokenService import TokenService

token_router = APIRouter(prefix="/token", tags=["token"])
security = HTTPBearer()
user_service = TokenService()
db_dep = Database()


JWT_SECRET = config("JWT_SECRET")
JWT_ALG = str(config("JWT_ALG", default="HS256"))


@token_router.post("/refresh")
async def refresh_token(dto: dict):
    token = dto.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="Missing refresh token")

    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])

        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return TokenService.create_tokens(user_id)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@token_router.post("/revoke")
async def revoke_refresh_token(
    data: dict,
    db: AsyncSession = Depends(db_dep.get_session),
    payload: dict = Depends(jwt_required)
):
    token_to_revoke = data.get("refresh_token")
    if not token_to_revoke:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing refresh_token"
        )

    query = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token_to_revoke,
            RefreshToken.user_id == payload.get("sub")
        )
    )
    refresh_rec = query.scalar()

    if not refresh_rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found"
        )

    refresh_rec.revoked = True
    await db.commit()

    return {"detail": "Refresh token revoked successfully"}