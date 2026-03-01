import os
import logging

import httpx

logger = logging.getLogger("uvicorn.error")

TELEGRAM_API = "https://api.telegram.org"


class TelegramService:
    def __init__(self):
        self.bot_token: str = ""
        self._client: httpx.AsyncClient | None = None

    async def init(self):
        self.bot_token = os.getenv("BOT_TOKEN", "")
        if not self.bot_token:
            logger.warning("[Telegram] BOT_TOKEN not set — notifications disabled")
            return

        self._client = httpx.AsyncClient(
            base_url=f"{TELEGRAM_API}/bot{self.bot_token}",
            timeout=httpx.Timeout(15.0),
        )
        logger.info("[Telegram] Notification service initialized")

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
        disable_notification: bool = False,
    ) -> bool:
        if not self._client:
            logger.warning("[Telegram] Service not initialized, skipping message")
            return False

        try:
            resp = await self._client.post(
                "/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_notification": disable_notification,
                },
            )

            if resp.status_code == 200 and resp.json().get("ok"):
                return True

            logger.error(
                f"[Telegram] sendMessage failed for chat {chat_id}: "
                f"{resp.status_code} — {resp.text}"
            )
            return False
        except Exception as e:
            logger.error(f"[Telegram] Error sending message to {chat_id}: {e}")
            return False

    async def send_recovery_code(self, chat_id: int, code: str) -> bool:
        text = (
            "<b>🔐 Код восстановления аккаунта</b>\n\n"
            f"<code>{code}</code>\n\n"
            "Сохраните этот код в надёжном месте.\n"
            "Он понадобится для восстановления доступа к аккаунту.\n\n"
            "<b>⚠️ Никому не передавайте этот код!</b>"
        )
        return await self.send_message(chat_id=chat_id, text=text)

    async def close(self):
        if self._client:
            await self._client.aclose()


telegram_service = TelegramService()
