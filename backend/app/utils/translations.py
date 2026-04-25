from __future__ import annotations

import logging
import os
import json
import time
import re
from pathlib import Path
from typing import Any
from random import uniform
from deep_translator import GoogleTranslator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | [translate][%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

LOCALES_DIR = Path("/app/data/locales")
SOURCE_LOCALE = "en"
TARGETS = [x.strip() for x in os.getenv("TARGET_LOCALES", "ru").split(",") if x.strip()]
MAX_BATCH_CHARS = 2500
MAX_RETRIES = 3
SEPARATOR = "[#@#]"

LANGUAGE_NAMES = {
    "en": "English",
    "ru": "Русский",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
    "it": "Italiano",
    "pt": "Português",
    "zh": "中文",
    "ja": "日本語"
}

def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
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

def protect_placeholders(text: str) -> tuple[str, list[str]]:
    """Заменяет {что-то} на [[0]], [[1]] и т.д., чтобы переводчик их не трогал."""
    placeholders = re.findall(r"\{.*?\}", text)
    protected_text = text
    for i, p in enumerate(placeholders):
        protected_text = protected_text.replace(p, f"[[{i}]]", 1)
    return protected_text, placeholders

def restore_placeholders(text: str, placeholders: list[str]) -> str:
    """Возвращает оригинальные плейсхолдеры на место."""
    restored_text = text
    for i, p in enumerate(placeholders):
        pattern = re.compile(rf"\[\[\s*{i}\s*\]\]")
        restored_text = pattern.sub(p, restored_text)
    return restored_text

def translate_batch(texts: list[str], source_lang: str, target_lang: str) -> list[str]:
    if not texts:
        return []

    protected_data = [protect_placeholders(t) for t in texts]
    protected_texts = [p[0] for p in protected_data]
    all_placeholders = [p[1] for p in protected_data]

    def process_result(translated_list: list[str]) -> list[str]:
        final = []
        for i, t_text in enumerate(translated_list):
            final.append(restore_placeholders(t_text, all_placeholders[i]))
        return final

    translator = GoogleTranslator(source=source_lang, target=target_lang)
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            combined_text = SEPARATOR.join(protected_texts)
            translated = translator.translate(combined_text)
            result = [t.strip() for t in translated.split(SEPARATOR)]
            
            if len(result) != len(texts):
                logger.warning(f"[{target_lang}] Mismatch! Expected {len(texts)}, got {len(result)}. Splitting...")
                mid = len(texts) // 2
                return translate_batch(texts[:mid], source_lang, target_lang) + \
                       translate_batch(texts[mid:], source_lang, target_lang)
                
            return process_result(result)
        except Exception as e:
            logger.error(f"Attempt {attempt} failed for [{target_lang}]: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(uniform(2, 4))
            else:
                logger.error(f"Batch failed after {MAX_RETRIES} attempts.")
    
    return ["TRANSLATION_ERROR"] * len(texts)

def sync_locale(target: str, lang_select_data: dict[str, str]) -> None:
    source_file = LOCALES_DIR / f"{SOURCE_LOCALE}.json"
    target_file = LOCALES_DIR / f"{target}.json"

    if not source_file.exists():
        logger.error(f"Source file {source_file} not found!")
        return

    source_flat = flatten(load_json(source_file))
    current_flat = flatten(load_json(target_file))

    for lang_code, lang_name in lang_select_data.items():
        current_flat[f"lang_select.{lang_code}"] = lang_name

    keys_to_translate = [
        k for k in source_flat 
        if k not in current_flat and not k.startswith("lang_select.")
    ]
    
    if keys_to_translate:
        logger.info(f"[{target}] Found {len(keys_to_translate)} keys to translate")
        
        batch_keys = []
        batch_values = []
        chars_count = 0
        
        for key in keys_to_translate:
            val = source_flat[key]
            if not val.strip():
                current_flat[key] = val
                continue

            if chars_count + len(val) + len(SEPARATOR) > MAX_BATCH_CHARS:
                translated_res = translate_batch(batch_values, SOURCE_LOCALE, target)
                for bk, bv in zip(batch_keys, translated_res):
                    current_flat[bk] = bv
                
                batch_keys, batch_values, chars_count = [], [], 0
                time.sleep(uniform(0.5, 1.2))

            batch_keys.append(key)
            batch_values.append(val)
            chars_count += len(val) + len(SEPARATOR)

        if batch_keys:
            translated_res = translate_batch(batch_values, SOURCE_LOCALE, target)
            for bk, bv in zip(batch_keys, translated_res):
                current_flat[bk] = bv
    stale_keys = [
        k for k in current_flat 
        if k not in source_flat and not k.startswith("lang_select.")
    ]
    for k in stale_keys:
        del current_flat[k]

    save_json(target_file, unflatten(dict(sorted(current_flat.items()))))
    logger.info(f"[{target}] Sync complete.")

def run() -> None:
    all_langs = sorted(list(set([SOURCE_LOCALE] + TARGETS)))
    lang_select_data = {
        code: LANGUAGE_NAMES.get(code, code) for code in all_langs
    }

    logger.info(f"Starting translation engine. Targets: {', '.join(TARGETS)}")
    
    source_file = LOCALES_DIR / f"{SOURCE_LOCALE}.json"
    if source_file.exists():
        data = load_json(source_file)
        data["lang_select"] = lang_select_data
        save_json(source_file, data)
        logger.info(f"[{SOURCE_LOCALE}] Updated lang_select in source file")

    for locale in TARGETS:
        if locale == SOURCE_LOCALE:
            continue
        sync_locale(locale, lang_select_data)
        
    logger.info("All tasks completed successfully.")

if __name__ == "__main__":
    run()