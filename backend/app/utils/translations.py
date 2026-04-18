from __future__ import annotations

import logging
import os
import json
import time
from pathlib import Path
from typing import Any
from random import uniform
from deep_translator import GoogleTranslator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

LOCALES_DIR = Path("/app/data/locales")
SOURCE_LOCALE = "en"
TARGETS = [x.strip() for x in os.getenv("TARGET_LOCALES", "ru").split(",") if x.strip()]

def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"Ошибка при чтении {path}: {e}")
        return {}

def save_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def flatten(data: dict[str, Any], prefix: str = "") -> dict[str, str]:
    result = {}
    for key, value in data.items():
        full = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten(value, full))
        else:
            result[full] = str(value)
    return result

def unflatten(items: dict[str, str]) -> dict[str, Any]:
    root = {}
    for path, value in items.items():
        node = root
        parts = path.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    return root

def sync_locale(target: str) -> None:
    source_file = LOCALES_DIR / f"{SOURCE_LOCALE}.json"
    target_file = LOCALES_DIR / f"{target}.json"

    if not source_file.exists():
        logger.error(f"Исходный файл {source_file} не найден")
        return

    source_flat = flatten(load_json(source_file))
    current_flat = flatten(load_json(target_file))

    keys_to_translate = [k for k in source_flat if k not in current_flat]
    
    if keys_to_translate:
        logger.info(f"[{target}] Найдено {len(keys_to_translate)} новых ключей")
        translator = GoogleTranslator(source=SOURCE_LOCALE, target=target)
        
        for key in keys_to_translate:
            text_to_translate = source_flat[key]
            if not text_to_translate.strip():
                continue
                
            try:
                translated_text = translator.translate(text_to_translate)
                current_flat[key] = translated_text
                logger.info(f"[{target}] Переведено: {key}")
                time.sleep(uniform(0.3, 0.8)) 
            except Exception as e:
                logger.error(f"[{target}] Ошибка при переводе ключа {key}: {e}")
                time.sleep(5)

    stale_keys = [k for k in current_flat if k not in source_flat]
    for k in stale_keys:
        del current_flat[k]
        logger.info(f"[{target}] Удален устаревший ключ: {k}")

    save_json(target_file, unflatten(dict(sorted(current_flat.items()))))
    logger.info(f"[{target}] Синхронизация завершена. Добавлено: {len(keys_to_translate)}, Удалено: {len(stale_keys)}")

def run() -> None:
    logger.info(f"Запуск транслятора. Целевые языки: {', '.join(TARGETS)}")
    for locale in TARGETS:
        sync_locale(locale)
    logger.info("Все задачи по локализации выполнены.")

if __name__ == "__main__":
    run()
