import hashlib
import hmac

from decouple import config
from urllib.parse import unquote_plus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from modules.db.models.User import User
from modules.schemes.user.CheckUserDto import UserDto


class UsersService:
    def __init__(self):
        pass

    async def get_by_telegram_id(
        self, db: AsyncSession, telegram_id: int
    ) -> User | None:
        query = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return query.scalar()

    async def curid_user(
        self,
        db: AsyncSession,
        dto: UserDto,
        telegram_id: int,
        username: str,
        firstname: str,
        photo: str | None,
    ) -> User | None:
        user_rec = await self.get_by_telegram_id(db, telegram_id=telegram_id)

        if not user_rec:
            user_rec = User(
                telegram_id=telegram_id,
                token_key=self._gen_token(dto.initData),
                name=firstname,
                username=username,
                avatar_url=photo,
            )
        else:
            user_rec.username = username
            user_rec.name = firstname
            user_rec.avatar_url = photo
        
        await db.commit()
        await db.refresh(user_rec)
        return user_rec
    

    @staticmethod
    def _gen_token(seed: str) -> str:
        return hashlib.sha256(seed.encode()).hexdigest()

    @staticmethod
    def check_telegram_auth(hash_str, init_data, token, c_str="WebAppData") -> bool:
        """
        Validates the data received from the Telegram web app, using the
        method documented here:
        https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
        """

        init_data = sorted(
            [
                chunk.split("=")
                for chunk in unquote_plus(init_data).split("&")
                if chunk[: len("hash=")] != "hash="
            ],
            key=lambda x: x[0],
        )
        init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

        secret_key = hmac.new(c_str.encode(), token.encode(), hashlib.sha256).digest()
        data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256)

        return data_check.hexdigest() == hash_str

    @staticmethod
    def check_admin_token(token: str) -> bool:
        return token == config("API_TOKEN")
