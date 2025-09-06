from datetime import datetime, timezone
import string
import random

from pocketbase import PocketBase
from decouple import config
from telebot import types

from modules.logging import logger


class PocketBaseClient:
    def __init__(self):
        try:
            self.pb = PocketBase(str(config("PB_URL")))
            admin_data = self.pb.admins.auth_with_password(
                str(config("ADMIN_EMAIL")), str(config("ADMIN_PASSWORD"))
            )
        except Exception as e:
            logger.error(f"PocketBaseClient error: {config('PB_URL')} {e}")
            raise Exception("Unable to connect to PocketBase")

        if not admin_data.is_valid:
            raise Exception("Invalid admin data")

        self.ensure_default_lang()

    @staticmethod
    def _gen_password(ln=12):
        return "".join(random.choices(string.ascii_letters + string.digits, k=ln))

    @staticmethod
    def _get_user_info(message):
        uid = message.chat.id
        if message.chat.type == "private":
            name = message.chat.first_name
        else:
            name = message.chat.title
        uname = getattr(message.chat, "username", None)
        return uid, uname, name

    def check_user(self, message: types.Message, avatar_url=None):
        tg_id, uname, name = self._get_user_info(message)
        now = datetime.now(timezone.utc).isoformat()

        try:
            user = self.pb.collection("users").get_first_list_item(f"telegram_id={tg_id}")
            self.pb.collection("users").update(user.id, {"last_seen": now})
            return user
        except Exception:
            email = f"{tg_id}@telegram.local"
            pwd = self._gen_password()

            env = self.pb.collection("env").get_first_list_item('bot_token!=""', {"expand": "default_lang"})
            lang_id = env.expand['default_lang'].id
            logger.debug(f"{env} {lang_id}")

            data = {
                "telegram_id": tg_id,
                "email": email,
                "password": pwd,
                "passwordConfirm": pwd,
                "username": uname or f"user{tg_id}",
                "name": name or "",
                "lang": lang_id,
                "avatar_url": avatar_url or "",
                "last_seen": now,
                "admin": False,
            }
            return self.pb.collection("users").create(data)

    def get_user(self, message):
        try:
            return self.pb.collection("users").get_first_list_item(f"telegram_id={message.chat.id}")
        except Exception:
            return None

    def change_lang(self, message, lang="en"):
        user = self.check_user(message)
        try:
            lang_rec = self.pb.collection("langs").get_first_list_item(f"alias='{lang}'")
            self.pb.collection("users").update(user.id, {"lang": lang_rec.id})
        except Exception as e:
            logger.error(f"change_lang error: {e}")

    def get_lang(self, message):
        self.check_user(message)
        try:
            user = self.pb.collection("users").get_first_list_item(
                f"telegram_id={message.chat.id}", {"expand": "lang"}
            )
            if user.expand and "lang" in user.expand:
                return user.expand["lang"].alias
        except Exception:
            pass
        return "en"

    def get_all_translations(self):
        langs = self.pb.collection("langs").get_full_list(batch=50)
        return {l.alias: {"lang_name": l.name, "data": l.data} for l in langs}

    def ensure_default_lang(self):
        langs = self.pb.collection("langs").get_full_list(batch=1)
        env = self.pb.collection("env").get_first_list_item('bot_token!=""')

        if langs:
            if not getattr(env, "default_lang", None):
                logger.info(f"Not Found default lang")
                self.pb.collection("env").update(env.id, {"default_lang": langs[0].id})
                logger.info(f"Default language set: {langs[0].alias}")
            return langs[0]

        logger.error("No default language found, creating new one")
        base_lang = {
            "alias": "en-us",
            "name": "🇺🇸 English",
            "data": {
                "message-id": {
                    "msg": [
                        "Hello @{user}, This is message with 2-rows inline button block \n",
                        "For help send /help or click the button!"
                    ],
                    "inline": {
                        "1": {
                            "/help": "command:help",
                            "/login": "command:login"
                        },
                        "2": {
                            "/info": "command:stats"
                        }
                    }
                },
                "message-id-2": {
                    "msg": "Message with 2-rows keyboard buttons",
                    "key": {
                        "1": ["Yes", "No"]
                    }
                },
                "answers": {
                    "yes": "yes",
                    "no": "no"
                },
                "cancel": ["/back", "/close", "/cancel"]
            }
        }

        lang = self.pb.collection("langs").create(base_lang)

        logger.info(f"Default language created: {lang.alias}")
        logger.info("Setting default language")
        self.pb.collection("env").update(env.id, {"default_lang": lang.id})

        return lang


dbclient = PocketBaseClient()
