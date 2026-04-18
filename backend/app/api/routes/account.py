import json
import logging
import uuid
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.database.database import NotFound, db_client
from app.middleware.auth import deny_bot, require_auth
from app.schemas.models import LinkYandexRequest, User as TgUser
from app.services.auth.AuthService import AuthUtils
from app.services.auth.YandexOAuthService import YandexOAuthService

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/account", tags=["account"])


@router.post(
    "/link/telegram/token",
    dependencies=[Depends(require_auth)],
    summary="Токен для привязки Telegram (заглушка)",
)
async def get_telegram_linking_token(request: Request):
    user_id = request.state.user_id

    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    try:
        token = str(uuid.uuid4())[:8].upper()
        return JSONResponse({"token": token}, status_code=200)
    except Exception as e:
        logger.error("Error generating linking token: %s", e)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


@router.post(
    "/link/telegram",
    dependencies=[Depends(require_auth), Depends(deny_bot)],
    summary="Привязать Telegram по initData",
)
async def link_telegram_account(
    request_data: dict,
    request: Request,
):
    user_id = request.state.user_id

    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    try:
        init_data = request_data.get("initData", "")
        if not init_data:
            return JSONResponse({"detail": "Missing initData"}, status_code=400)

        parsed = {k: v[0] for k, v in parse_qs(init_data).items()}

        if not parsed.get("hash"):
            return JSONResponse({"detail": "Missing initData hash"}, status_code=400)

        if not AuthUtils.check_initdata(initdata=init_data, hash_str=parsed["hash"]):
            return JSONResponse({"detail": "InitData validation failed"}, status_code=401)

        try:
            user_data = TgUser(**json.loads(parsed["user"]))
        except ValidationError:
            return JSONResponse({"detail": "Invalid Telegram data"}, status_code=400)

        await db_client.link_user_telegram(str(user_id), user_data.id)
        return JSONResponse({"detail": "Telegram linked successfully"}, status_code=200)

    except Exception as e:
        logger.error("Error linking Telegram: %s", e)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


@router.post(
    "/link/yandex",
    dependencies=[Depends(require_auth)],
    summary="Привязать Yandex по коду OAuth",
)
async def link_yandex_account(
    request_data: LinkYandexRequest,
    request: Request,
):
    user_id = request.state.user_id

    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    try:
        code = request_data.code
        if not code:
            return JSONResponse({"detail": "Missing authorization code"}, status_code=400)

        oauth_service = YandexOAuthService()

        auth_result = await oauth_service.authenticate_user(code)
        if not auth_result:
            return JSONResponse(
                {"detail": "Failed to authenticate with Yandex"}, status_code=401
            )

        user_info = auth_result["user_info"]
        yandex_id = user_info.get("id")

        if not yandex_id:
            return JSONResponse({"detail": "Invalid Yandex response"}, status_code=400)

        await db_client.link_user_yandex(str(user_id), str(yandex_id))

        return JSONResponse({"detail": "Yandex linked successfully"}, status_code=200)

    except ValueError as e:
        logger.error("Yandex OAuth configuration error: %s", e)
        return JSONResponse({"detail": "OAuth service not configured"}, status_code=500)
    except Exception as e:
        logger.error("Error linking Yandex account: %s", e)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


@router.post(
    "/unlink/{provider}",
    dependencies=[Depends(require_auth)],
    summary="Отвязать провайдера",
)
async def unlink_account(
    provider: str,
    request: Request,
):
    user_id = request.state.user_id

    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    if provider not in ["telegram", "yandex"]:
        return JSONResponse({"detail": "Invalid provider"}, status_code=400)

    try:
        user = await db_client.get_user(uid=str(user_id))

        if provider == "telegram":
            if not user.linked_yandex:
                return JSONResponse(
                    {"detail": "Cannot unlink your only authentication method"},
                    status_code=400,
                )
            await db_client.unlink_telegram(user.id)
        elif provider == "yandex":
            if not user.linked_telegram:
                return JSONResponse(
                    {"detail": "Cannot unlink your only authentication method"},
                    status_code=400,
                )
            await db_client.unlink_yandex(user.id)

        return JSONResponse(
            {"detail": f"{provider} unlinked successfully"}, status_code=200
        )

    except NotFound:
        return JSONResponse({"detail": "User not found"}, status_code=404)
    except Exception as e:
        logger.error("Error unlinking %s: %s", provider, e)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


@router.delete(
    "",
    dependencies=[Depends(require_auth)],
    summary="Удалить аккаунт",
)
async def delete_account(request: Request):
    user_id = request.state.user_id

    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    try:
        await db_client.delete_user(user_id=str(user_id))
        return JSONResponse({"detail": "Account deleted successfully"}, status_code=200)
    except NotFound:
        return JSONResponse({"detail": "User not found"}, status_code=404)
    except Exception as e:
        logger.error("Error deleting account: %s", e)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)
