import json
import re
from pathlib import Path

from app.middleware.spam import rate_limit
from app.services.caching import cache
from app.utils.translations import LANGUAGE_NAMES
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from pathlib import Path

router = APIRouter(prefix="/languages", tags=["system"])
LOCALES_DIR = Path("/app/data/locales")


def _locale_files_map() -> dict[str, Path]:
    return {file.stem.lower(): file.resolve() for file in LOCALES_DIR.glob("*.json") if file.is_file()}


def get_locale_file(locale: str) -> Path:
    normalized_locale = locale.split("-")[0].lower()
    if not re.fullmatch(r"[a-z]{2,10}", normalized_locale):
        raise HTTPException(status_code=400, detail="Invalid locale")
    if normalized_locale not in LANGUAGE_NAMES:
        raise HTTPException(status_code=400, detail="Language not supported")

    locale_files = _locale_files_map()
    locale_file = locale_files.get(normalized_locale)
    if locale_file is None:
        raise HTTPException(status_code=404, detail="Locale not found")

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

@cache()
@rate_limit(limit=10, period=120)
@router.get("/get/{locale}", summary="Получить перевод для языка")
def get_language(locale: str):
    normalized = locale.split('-')[0].lower()
    
    if normalized not in LANGUAGE_NAMES.keys():
        return JSONResponse({"error": "Language not supported"}, status_code=400)
    
    locale_file = get_locale_file(normalized)
    with locale_file.open('r', encoding='utf-8') as fp:
        data = json.load(fp)
    return JSONResponse(data, status_code=200)
