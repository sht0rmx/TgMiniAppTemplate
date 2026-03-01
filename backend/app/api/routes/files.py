from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import JSONResponse, Response

from app.database.database import NotFound, db_client
from app.middleware.auth import deny_bot, require_auth, require_origin

router = APIRouter(prefix="/files", tags=["files"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.get(
    "/all",
    dependencies=[Depends(require_origin), Depends(deny_bot()), Depends(require_auth)],
)
async def list_files(request: Request):
    user_id = request.state.user_id
    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    try:
        files = await db_client.get_files(user_id=user_id)
    except Exception:
        files = []

    result = [
        {
            "id": str(f.id),
            "name": str(f.key).split("/")[-1] if "/" in str(f.key) else str(f.key),
            "key": str(f.key),
            "uploadedAt": f.uploaded_at.isoformat() if f.uploaded_at else "",
        }
        for f in files
    ]

    return JSONResponse({"files": result}, status_code=200)


@router.post(
    "/upload",
    dependencies=[Depends(require_origin), Depends(deny_bot()), Depends(require_auth)],
)
async def upload_file(request: Request, file: UploadFile = File(...)):
    user_id = request.state.user_id
    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    if not file.filename:
        return JSONResponse({"detail": "No filename"}, status_code=400)

    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        return JSONResponse(
            {"detail": f"File too large. Max {MAX_FILE_SIZE // (1024*1024)} MB"},
            status_code=400,
        )

    try:
        await db_client.upload_file(
            user_id=user_id, data=data, filename=file.filename
        )
        return JSONResponse({"detail": "uploaded"}, status_code=201)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.get(
    "/{file_id}",
    dependencies=[Depends(require_origin), Depends(deny_bot()), Depends(require_auth)],
)
async def download_file(request: Request, file_id: str):
    user_id = request.state.user_id
    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    try:
        # Verify ownership
        files = await db_client.get_files(user_id=user_id)
        target = next((f for f in files if str(f.id) == file_id), None)
        if not target:
            return JSONResponse({"detail": "File not found"}, status_code=404)

        data = await db_client.get_file(file_id=file_id, key="")
        filename = str(target.key).split("/")[-1] if "/" in str(target.key) else str(target.key)

        return Response(
            content=data,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except NotFound:
        return JSONResponse({"detail": "File not found"}, status_code=404)


@router.delete(
    "/{file_id}",
    dependencies=[Depends(require_origin), Depends(deny_bot()), Depends(require_auth)],
)
async def delete_file(request: Request, file_id: str):
    user_id = request.state.user_id
    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    try:
        # Verify ownership
        files = await db_client.get_files(user_id=user_id)
        target = next((f for f in files if str(f.id) == file_id), None)
        if not target:
            return JSONResponse({"detail": "File not found"}, status_code=404)

        await db_client.delete_file(file_id=file_id)
        return JSONResponse({"detail": "deleted"}, status_code=200)
    except NotFound:
        return JSONResponse({"detail": "File not found"}, status_code=404)
