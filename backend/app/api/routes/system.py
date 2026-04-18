import json
from pathlib import Path

from app.middleware.spam import rate_limit
from app.services.caching import cache
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from pathlib import Path

router = APIRouter(prefix="/languages", tags=["system"])
LOCALES_DIR = Path("/app/data/locales")


def get_locale_file(locale: str) -> Path:
    locale_file = LOCALES_DIR / f"{locale}.json"

    if not locale_file.exists() or not locale_file.is_file():
        raise HTTPException(status_code=404, detail="Locale not found")

    return locale_file

@cache(ttl=3600)
@router.get("/list", summary="Список доступных языков")
def get_languages():
    languages = []
    
    for file in sorted(LOCALES_DIR.glob("*.json")):
        languages.append({
            "id": file.stem,
            "name": file.stem,
        })

    return JSONResponse(
        content={"languages": languages},
        status_code=200,
    )

@cache
@rate_limit(limit=10, period=120)
@router.get("/get/{locale}", summary="Получить перевод для языка")
def get_language(locale: str):
    normalized = locale.split('-')[0]
    locale_file = get_locale_file(normalized)
    with locale_file.open('r', encoding='utf-8') as fp:
        data = json.load(fp)
    return JSONResponse(data, status_code=200)
