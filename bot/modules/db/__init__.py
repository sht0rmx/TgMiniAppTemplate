from datetime import datetime, timezone
from pocketbase import PocketBase
from decouple import config
import string
import random


class PocketBaseClient:
    pb = PocketBase(str(config("PB_URL")))

    def __init__(self):
        admin_data = self.pb.admins.auth_with_password(
            str(config("ADMIN_EMAIL")), str(config("ADMIN_PASSWORD"))
        )

        if not admin_data.is_valid:
            raise Exception("Invalid admin data")

    def create_user(self, tg_id: int, username: str, name: str, avatar_url: str):
        try:
            u = self.pb.collection("users").get_first_list_item(f"telegram_id={tg_id}")
            return u
        except Exception:
            pass

        email = f"{tg_id}@telegram.local"
        _pass = "".join(random.choices(string.ascii_letters + string.digits, k=12))

        data = {
            "telegram_id": tg_id,
            "email": email,
            "password": _pass,
            "passwordConfirm": _pass,
            "username": username or f"user{tg_id}",
            "name": name or "",
            "avatar_url": avatar_url or "",
        }

        u = self.pb.collection("users").create(data)
        return u

    def update_last_seen(self, uid: str):
        now = datetime.now(timezone.utc).isoformat()
        self.pb.collection("users").update(uid, {"last_seen": now})

    def get_all_translations(self):
        all_list = self.pb.collection("langs").get_full_list(batch=50)

        cash = {}
        for lang in all_list:
            cash[lang.alias] = {"lang_name": lang.name, "data": lang.data}

        return cash

    def get_lang(self, uid):
        lang = self.pb.collection("settings").get_first_list_item(f"telegram_id={uid}")

        if not lang:
            raise Exception("No language found")

        return lang.alias

dbclient = PocketBaseClient()
