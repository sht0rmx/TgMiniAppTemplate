import json
import os

from utils import logger


class TranslationManager:
    def __init__(self, path="locales"):
        self.path = path
        self.data = {}
        self.load_all()

    def load_all(self):
        try:
            for file in os.listdir(self.path):
                if file.endswith(".json"):
                    with open(os.path.join(self.path, file), "r", encoding="utf-8") as f:
                        lang = json.load(f)
                        alias = lang.get("lang-alias")
                        if alias:
                            self.data[alias] = lang
            logger.info(f"Loaded {len(self.data)} language packs")
        except Exception as e:
            logger.error(f"Error loading translations: {e}")

    def t(self, message, msg_id, lang="en"): # FIXME if message from callback selects en lang by default!
        try:
            user_lang = getattr(message.from_user, "language_code", lang) or lang
            lang_data = self.data.get(user_lang[:2], self.data.get(lang))
            if not lang_data:
                logger.warning(f"Lang '{user_lang}' not found, fallback to '{lang}'")
                return None
            return lang_data["messages"].get(msg_id)
        except Exception as e:
            logger.error(f"Error getting translation '{msg_id}': {e}")
            return None


translations = TranslationManager()
