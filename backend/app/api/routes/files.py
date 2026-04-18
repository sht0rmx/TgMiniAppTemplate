import io
import mimetypes
from typing import Optional

from fastapi import APIRouter, Depends, Request, UploadFile, File, Header
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel

from app.database.database import NotFound, db_client
from app.middleware.auth import deny_bot, require_auth


class RenameFileRequest(BaseModel):
    name: str

router = APIRouter(prefix="/files", tags=["files"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def iter_file(data: bytes, start: int, end: int, chunk_size: int = 1024 * 1024):
    stream = io.BytesIO(data)
    stream.seek(start)

    remaining = end - start + 1
    while remaining > 0:
        read_size = min(chunk_size, remaining)
        chunk = stream.read(read_size)
        if not chunk:
            break
        remaining -= len(chunk)
        yield chunk


@router.get(
    "/all",
    dependencies=[Depends(deny_bot), Depends(require_auth)],
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
            "name": f.display_name,
            "key": str(f.key),
            "uploadedAt": f.uploaded_at.isoformat() if f.uploaded_at else "",
        }
        for f in files
    ]

    return JSONResponse({"files": result}, status_code=200)


@router.post(
    "/upload",
    dependencies=[Depends(deny_bot), Depends(require_auth)],
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
    dependencies=[Depends(deny_bot), Depends(require_auth)],
)
async def download_file(request: Request, file_id: str):
    u = request.state.user_id
    if not u:
        return JSONResponse({"detail": "no_uid"}, 400)

    try:
        f_list = await db_client.get_files(user_id=u)
        t = next((f for f in f_list if str(f.id) == file_id), None)
        if not t:
            return JSONResponse({"detail": "404"}, 404)

        # Получаем данные целиком
        d = await db_client.get_file(file_id=file_id, key="")
        s = len(d)
        name = t.display_name
        
        m, _ = mimetypes.guess_type(name)
        m = m or "application/octet-stream"

        h = {
            "Content-Disposition": f'inline; filename="{name}"',
            "Content-Length": str(s),
            "Accept-Ranges": "bytes",
            "Access-Control-Expose-Headers": "Content-Length, Content-Disposition",
        }

        print(f"Full send: {name} ({s} bytes)")
        
        return Response(
            content=d,
            media_type=m,
            status_code=200,
            headers=h
        )

    except NotFound:
        return JSONResponse({"detail": "404"}, 404)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, 500)
    
    
@router.delete(
    "/{file_id}",
    dependencies=[Depends(deny_bot), Depends(require_auth)],
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


@router.put(
    "/{file_id}/rename",
    dependencies=[Depends(deny_bot), Depends(require_auth)],
)
async def rename_file(request: Request, file_id: str, body: RenameFileRequest):
    user_id = request.state.user_id
    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    if not body.name or not body.name.strip():
        return JSONResponse({"detail": "Invalid name"}, status_code=400)

    try:
        # Verify ownership
        files = await db_client.get_files(user_id=user_id)
        target = next((f for f in files if str(f.id) == file_id), None)
        if not target:
            return JSONResponse({"detail": "File not found"}, status_code=404)

        await db_client.rename_file(file_id=file_id, new_name=body.name.strip())
        return JSONResponse({"detail": "renamed", "name": body.name.strip()}, status_code=200)
    except NotFound:
        return JSONResponse({"detail": "File not found"}, status_code=404)
