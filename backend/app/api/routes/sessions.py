from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.database.database import NotFound, db_client
from app.middleware.auth import deny_bot, require_auth, require_origin
from app.utils import parse_user_agent_data

router = APIRouter(prefix="/session", tags=["Sessions"])


@router.get("/current", dependencies=[Depends(require_origin), Depends(require_auth)])
async def current_session(request: Request):
    session_id = request.state.session_id
    fingerprint = request.state.fingerprint

    if not session_id:
        return JSONResponse({"detail": "session id not found"}, status_code=400)

    session = await db_client.get_refresh_session(fingerprint=fingerprint)

    info = parse_user_agent_data(str(session.user_agent))
    return JSONResponse(
        {
            "ip": session.ip,
            "lastUsed": session.used_at.isoformat(),
            "info": info,
            "session": str(session.id),
        }
    )


@router.get("/all", dependencies=[Depends(require_origin), Depends(require_auth)])
async def all_sessions(request: Request):
    user_id = request.state.user_id
    current_session_id = request.state.session_id

    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    try:
        sessions = await db_client.get_all_sessions(user_id=user_id)
    except NotFound:
        return JSONResponse({"sessions": [], "current_session": current_session_id}, status_code=200)

    result = []
    for s in sessions:
        info = parse_user_agent_data(str(s.user_agent))
        result.append(
            {
                "id": str(s.id),
                "ip": s.ip,
                "lastUsed": s.used_at.isoformat(),
                "createdAt": s.created_at.isoformat(),
                "info": info,
                "isCurrent": str(s.id) == str(current_session_id),
            }
        )

    return JSONResponse(
        {"sessions": result, "current_session": str(current_session_id)},
        status_code=200,
    )


@router.get(
    "/kill/{sid}", dependencies=[Depends(require_origin), Depends(deny_bot())]
)
async def kill_session(request: Request, sid: str):
    user_id = request.state.user_id
    current_session_id = request.state.session_id

    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    if str(sid) == str(current_session_id):
        return JSONResponse(
            {"detail": "Cannot terminate current session"}, status_code=400
        )

    try:
        await db_client.delete_refresh_session_by_id(
            session_id=sid, user_id=user_id
        )
        return JSONResponse({"detail": "Session terminated"}, status_code=200)
    except NotFound:
        return JSONResponse({"detail": "Session not found"}, status_code=404)
