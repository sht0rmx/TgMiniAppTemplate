import hashlib
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import and_, delete, insert, or_, select, update
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from sqlalchemy.sql.expression import Select

from app.database.models import Base
from app.database.models.ApiKeys import ApiKey
from app.database.models.Files import File
from app.database.models.OneTimeCodes import OneTimeCode
from app.database.models.RecoveryCodes import RecoveryCode
from app.database.models.RefreshSessions import RefreshSession
from app.database.models.Users import User
from app.storage.storage import StorageClient
from app.utils import create_hash, is_date_expired, parse_expire

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(str(DATABASE_URL), echo=False)


class DBError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NotFound(DBError):
    pass


class Revoked(DBError):
    pass


class Expired(DBError):
    pass


class Banned(DBError):
    pass


class NewRecord(DBError):
    pass


class AlreadyCreated(DBError):
    pass


class NotEnoughValues(DBError):
    pass


class Database:
    def __init__(self):
        self.engine = engine
        self.storage = StorageClient()
        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def get_refresh_session(
        self, refresh_token: str = "", fingerprint: str = "", session_id: str = ""
    ) -> RefreshSession:
        token_hash = (
            create_hash("REFRESH_SECRET", refresh_token) if refresh_token else None
        )

        async with self.async_session() as dbsession:
            conditions = [RefreshSession.fingerprint == fingerprint]

            if token_hash:
                conditions.append(RefreshSession.refresh_token_hash == token_hash)
            if session_id:
                conditions.append(RefreshSession.id == session_id)

            result = await dbsession.execute(
                select(RefreshSession).where(and_(*conditions))
            )
            session = result.scalars().first()

            if not session:
                raise NotFound("Session not found with given parameters")

            if bool(session.revoked):
                raise Revoked("Session was revoked")

            if is_date_expired(
                created=session.used_at, expire_delta=os.getenv("REFRESH_EXPIRE", "60d")
            ):
                raise Expired("Session expired")

            return session

    async def get_all_sessions(self, user_id:str | uuid.UUID) -> list[RefreshSession]:
        async with self.async_session() as dbsession:
            result = await dbsession.execute(
                select(RefreshSession).where(and_(
                    RefreshSession.user_id == str(user_id),
                    RefreshSession.revoked == False))
            )
            sessions = result.scalars().all()

            if not sessions:
                raise NotFound("Sessions not found with given parameters")

            sessions = [
                s for s in sessions
                if not is_date_expired(
                    created=s.used_at, expire_delta=os.getenv("REFRESH_EXPIRE", "60d")
                )
            ]

            return sessions

    async def get_user(
        self,
        uid: str | uuid.UUID = "",
        telegram_id: int = 0,
        username: str = "",
        yandex_id: str = "",
    ) -> User:
        async with self.async_session() as dbsession:
            query = select(User)

            if uid:
                query = query.where(User.id == uid)
            elif telegram_id:
                query = query.where(User.telegram_id == telegram_id)
            elif username:
                query = query.where(User.username == username)
            elif yandex_id:
                query = query.where(User.yandex_id == yandex_id)

            result = await dbsession.execute(query)
            user = result.scalars().first()

            if not user:
                raise NotFound("User not found")

            return user

    async def get_login_session(self, code: str = "", login_hash: str = "") -> OneTimeCode:
        if code:
            code_hash = create_hash("LOGIN_SECRET", code.lower())
            query = select(OneTimeCode).where(OneTimeCode.code_hash == code_hash)
            return await self.get_login_session_query(query)
        elif login_hash:
            query = select(OneTimeCode).where(OneTimeCode.login_id == login_hash)
            return await self.get_login_session_query(query)

        raise NotFound("Login session not found")

    async def get_login_session_query(self, query: Select) -> OneTimeCode:
        async with self.async_session() as dbsession:
            result = await dbsession.execute(query)
            login_session = result.scalars().first()

            if not login_session:
                raise NotFound("login session not found")

            if is_date_expired(
                created=login_session.created_at,
                expire_delta=str(os.getenv("LOGIN_EXPIRE")),
            ):
                raise Expired("Login session expired!")

            return login_session

    async def set_one_time_code_accepted(
        self, login_session_id: str | uuid.UUID
    ) -> OneTimeCode:
        async with self.async_session() as dbsession:
            res = await dbsession.execute(
                update(OneTimeCode)
                .values(accepted=True)
                .where(OneTimeCode.id == login_session_id)
                .returning(OneTimeCode)
            )
            await dbsession.commit()
            row = res.scalar_one_or_none()
            if not row:
                raise NotFound("Login session not found")
            return row

    async def get_recovery_code(
        self, hash: str = "", user_id: str | uuid.UUID = ""
    ) -> RecoveryCode:
        async with self.async_session() as dbsession:
            query = select(RecoveryCode)

            if hash:
                query = query.where(RecoveryCode.code_hash == hash)
            elif user_id:
                query = query.where(RecoveryCode.user_id == user_id)

            result = await dbsession.execute(query)
            code = result.scalars().first()

            if not code:
                raise NotFound("Recovery code for this user not found!")

            return code

    async def get_api_key(self, hash: str = "", api_key_id: str = "") -> ApiKey:
        async with self.async_session() as dbsession:
            query = select(ApiKey)

            if api_key_id:
                query = query.where(ApiKey.id == api_key_id)
            elif hash:
                query = query.where(ApiKey.api_key_hash == hash)
            else:
                raise ValueError("Either hash or api_key_id must be provided")

            result = await dbsession.execute(query)
            api_key = result.scalar_one_or_none()

            if not api_key:
                raise NotFound("API key not found")
            if bool(api_key.banned):
                raise Banned("API key is blocked")

            return api_key

    async def get_api_keys_for_user(self, user_id: str) -> list[ApiKey]:
        async with self.async_session() as dbsession:
            query = select(ApiKey).where(ApiKey.user_id == user_id)
            result = await dbsession.execute(query)
            api_keys = list(result.scalars().all())

            if len(api_keys) == 0:
                raise NotFound("ApiKeys not founded")

            return api_keys

    async def get_files(self, user_id: str | uuid.UUID, limit: int = 100) -> list[File]:
        async with self.async_session() as dbsession:
            result = await dbsession.execute(
                select(File).where(File.uploaded_by == user_id).limit(limit)
            )
            return list(result.scalars().all())

    async def get_file(self, file_id: str, key: str) -> bytes:
        if file_id:
            async with self.async_session() as dbsession:
                result = await dbsession.execute(select(File).where(File.id == file_id))
                key = str(result.scalar_one().key)

        return await self.storage.download_file(key=key)

    async def update_refresh_session(
        self, fingerprint: str, ip: str, rt_key: str, new_rt_key: str = ""
    ) -> RefreshSession:
        async with self.async_session() as dbsession:
            session = await self.get_refresh_session(fingerprint=fingerprint, refresh_token=rt_key)

            values: dict = {"ip": ip, "used_at": datetime.now()}

            if new_rt_key:
                values["refresh_token_hash"] = create_hash("REFRESH_SECRET", new_rt_key)

            query = (
                update(RefreshSession)
                .values(**values)
                .where(RefreshSession.id == session.id)
                .returning(RefreshSession)
            )

            res = await dbsession.execute(query)
            session = res.scalar_one_or_none()

            if not session:
                raise NotFound("Session with params not founded")

            await dbsession.commit()
            return session

    async def update_user(
        self,
        telegram_id: int,
        username: str | None,
        name: str | None,
        avatar_url: str | None,
        role="user",
    ) -> tuple[User, bool]:
        async with self.async_session() as dbsession:
            res = await dbsession.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = res.scalar_one_or_none()

            if user:
                vals = {
                    "username": username or user.username,
                    "name": name or user.name,
                    "role": role or user.role,
                    "avatar_url": avatar_url or user.avatar_url,
                    "last_seen": datetime.now(),
                }

                res = await dbsession.execute(
                    update(User)
                    .where(User.id == user.id)
                    .values(**vals)
                    .returning(User)
                )
                await dbsession.commit()
                return res.scalar_one(), False

            if not any([username, name, avatar_url, role]):
                raise NotEnoughValues("Not enough values to create object")

            res = await dbsession.execute(
                insert(User)
                .values(
                    telegram_id=telegram_id,
                    username=username,
                    name=name,
                    role=role,
                    avatar_url=avatar_url,
                    last_seen=datetime.now(),
                )
                .returning(User)
            )
            await dbsession.commit()
            return res.scalar_one(), True

    async def update_user_id(self, old_id, new_id):
        async with self.async_session() as dbsession:
            await dbsession.execute(
                update(User).values(id=new_id).where(User.id == old_id)
            )

            await dbsession.commit()
            return True

    async def link_user_telegram(
        self, user_id: str | uuid.UUID, telegram_id: int
    ) -> None:
        async with self.async_session() as dbsession:
            res = await dbsession.execute(
                update(User)
                .where(User.id == user_id)
                .values(telegram_id=telegram_id, linked_telegram=True)
            )
            if res.rowcount == 0:
                raise NotFound("User not found")
            await dbsession.commit()

    async def link_user_yandex(
        self, user_id: str | uuid.UUID, yandex_id: str
    ) -> None:
        async with self.async_session() as dbsession:
            res = await dbsession.execute(
                update(User)
                .where(User.id == user_id)
                .values(yandex_id=str(yandex_id), linked_yandex=True)
            )
            if res.rowcount == 0:
                raise NotFound("User not found")
            await dbsession.commit()

    async def unlink_telegram(self, user_id: str | uuid.UUID) -> None:
        async with self.async_session() as dbsession:
            res = await dbsession.execute(
                update(User)
                .where(User.id == user_id)
                .values(linked_telegram=False)
            )
            if res.rowcount == 0:
                raise NotFound("User not found")
            await dbsession.commit()

    async def unlink_yandex(self, user_id: str | uuid.UUID) -> None:
        async with self.async_session() as dbsession:
            res = await dbsession.execute(
                update(User)
                .where(User.id == user_id)
                .values(linked_yandex=False, yandex_id=None)
            )
            if res.rowcount == 0:
                raise NotFound("User not found")
            await dbsession.commit()

    async def update_api_key(self, key_id: str, banned=False):
        async with self.async_session() as dbsession:
            await dbsession.execute(
                update(ApiKey).values(banned=banned).where(ApiKey.id == key_id)
            )

            await dbsession.commit()
            return True

    async def upload_file(self, user_id: str | uuid.UUID, data: bytes, filename: str) -> bool:
        key = await self.storage.upload_file(
            key=f"{user_id}/{uuid.uuid4()}-{filename}", data=data
        )

        async with self.async_session() as dbsession:
            await dbsession.execute(insert(File).values(uploaded_by=user_id, key=key, display_name=filename))
            await dbsession.commit()
            return True

    async def create_refresh_session(self, refresh_token: str, fingerprint: str, ip: str, user_id: str | uuid.UUID, user_agent: str = "") -> RefreshSession:
        async with self.async_session() as dbsession:
            token_hash = create_hash("REFRESH_SECRET", str(refresh_token))

            await self.delete_refresh_session(fingerprint=fingerprint)
            query = (
                insert(RefreshSession)
                .values(
                    refresh_token_hash=token_hash,
                    fingerprint=fingerprint,
                    ip=ip,
                    user_id=user_id,
                    user_agent=user_agent,
                )
                .returning(RefreshSession)
            )

            res = await dbsession.execute(query)
            await dbsession.commit()
            return res.scalar_one()

    async def create_login_session(self, code: str, fingerprint: str, ip: str) -> tuple[str, str]:
        async with self.async_session() as dbsession:
            code = code.lower()
            login_id = create_hash(fingerprint, code, from_env=False)
            login_hash = create_hash("LOGIN_SECRET", str(login_id))
            code_hash = create_hash("LOGIN_SECRET", code)

            await dbsession.execute(
                insert(OneTimeCode).values(
                    fingerprint=fingerprint,
                    login_id=login_hash,
                    code_hash=code_hash,
                    sse_login_id=str(login_id),
                    ip=ip,
                )
            )

            await dbsession.commit()
            return str(login_id), code

    async def create_recovery_code(self, user_id: str | uuid.UUID, code: str) -> bool:
        async with self.async_session() as dbsession:
            try:
                code = await self.get_recovery_code(user_id=user_id)
                raise AlreadyCreated("Recovery code can be generated only one time")
            except NotFound:
                code_hash = create_hash("RECOVERY_SECRET", code)
                await dbsession.execute(
                    insert(RecoveryCode).values(user_id=user_id, code_hash=code_hash)
                )

                await dbsession.commit()
                return True

    async def create_api_key(self, user_id: str, name: str, api_key: str):
        async with self.async_session() as dbsession:
            if not api_key.startswith("sk_"):
                raise ValueError("Api key must starts with `sk_`")

            key_hash = create_hash("API_SECRET", api_key)

            await dbsession.execute(
                insert(ApiKey).values(user_id=user_id, name=name, api_key_hash=key_hash)
            )

            await dbsession.commit()
            return True

    async def delete_user(self, user_id: str | uuid.UUID) -> bool:
        async with self.async_session() as dbsession:
            try:
                user = await self.get_user(uid=user_id)

                await dbsession.execute(
                    delete(RefreshSession).where(RefreshSession.user_id == user.id)
                )
                await dbsession.execute(
                    delete(RecoveryCode).where(RecoveryCode.user_id == user.id)
                )
                await dbsession.execute(
                    delete(ApiKey).where(ApiKey.user_id == user.id)
                )
                await dbsession.execute(
                    delete(File).where(File.uploaded_by == user.id)
                )
                await dbsession.execute(delete(User).where(User.id == user.id))

                await dbsession.commit()
                return True
            except NotFound:
                raise NotFound("User for deletion not found!")

    async def delete_refresh_session(self, fingerprint: str):
        async with self.async_session() as dbsession:
            await dbsession.execute(
                delete(RefreshSession).where(RefreshSession.fingerprint == fingerprint)
            )
            await dbsession.commit()
            return True

    async def delete_refresh_session_by_id(self, session_id: str, user_id: str | uuid.UUID):
        async with self.async_session() as dbsession:
            result = await dbsession.execute(
                delete(RefreshSession)
                .where(
                    and_(
                        RefreshSession.id == session_id,
                        RefreshSession.user_id == str(user_id),
                    )
                )
                .returning(RefreshSession.id)
            )
            deleted = result.scalar_one_or_none()
            if not deleted:
                raise NotFound("Session not found")
            await dbsession.commit()
            return True

    async def delete_api_key(self, key_id: str):
        async with self.async_session() as dbsession:
            await dbsession.execute(delete(ApiKey).where(ApiKey.id == key_id))
            await dbsession.commit()
            return True

    async def delete_file(self, file_id: str | uuid.UUID) -> bool:
        async with self.async_session() as db:
            result = await db.execute(select(File).where(File.id == file_id))
            file_record = result.scalars().first()

            if not file_record:
                raise NotFound("File not found!")

            await self.storage.delete_file(key=str(file_record.key))

            await db.execute(delete(File).where(File.id == file_id))
            await db.commit()
            return True

    async def rename_file(self, file_id: str | uuid.UUID, new_name: str) -> bool:
        async with self.async_session() as db:
            result = await db.execute(select(File).where(File.id == file_id))
            file_record = result.scalars().first()

            if not file_record:
                raise NotFound("File not found!")

            await db.execute(update(File).where(File.id == file_id).values(display_name=new_name))
            await db.commit()
            return True

    async def find_or_create_yandex_user(
        self,
        yandex_id: str,
        username: str,
        name: str,
        avatar_url: str | None,
        email: str = "",
    ) -> tuple[User, bool]:
        user = None
        is_new = False

        try:
            user = await self.get_user(yandex_id=str(yandex_id))
        except NotFound:
            user = None

        if user is None and username:
            try:
                existing_by_username = await self.get_user(username=username)
                if not existing_by_username.yandex_id:
                    user = existing_by_username
                elif existing_by_username.yandex_id == str(yandex_id):
                    user = existing_by_username
            except NotFound:
                pass

        if user is None:
            candidate_username = username or None
            if candidate_username:
                try:
                    await self.get_user(username=candidate_username)
                    suffix = 1
                    base_username = candidate_username
                    while True:
                        candidate_username = f"{base_username}_{suffix}"
                        try:
                            await self.get_user(username=candidate_username)
                            suffix += 1
                        except NotFound:
                            break
                except NotFound:
                    pass

            fake_telegram_id = -(
                int(
                    hashlib.sha256(
                        str(yandex_id or username or email).encode()
                    ).hexdigest(),
                    16,
                )
                % (10**17)
            ) - 1

            user, is_new = await self.update_user(
                telegram_id=fake_telegram_id,
                username=candidate_username,
                name=name,
                avatar_url=avatar_url,
            )
        else:
            user, _ = await self.update_user(
                telegram_id=user.telegram_id,
                username=username or user.username,
                name=name,
                avatar_url=avatar_url,
            )

        return user, is_new

    async def recovery_user(self, code: str, user_id: str | uuid.UUID) -> bool:
        async with self.async_session() as dbsession:
            try:
                hash = create_hash("RECOVERY_SECRET", code)
                recovery_code = await self.get_recovery_code(hash=str(hash))
                
                old_user = await self.get_user(uid=str(recovery_code.user_id))
                current_user = await self.get_user(uid=str(user_id))

                await dbsession.execute(delete(RefreshSession).where(RefreshSession.user_id == old_user.id))
                await dbsession.execute(delete(RecoveryCode).where(RecoveryCode.user_id == old_user.id))
                await dbsession.execute(delete(User).where(User.id == old_user.id))

                await dbsession.execute(
                    update(User).where(User.id == current_user.id).values(
                        username=old_user.username,
                        name=old_user.name,
                        role=old_user.role,
                        avatar_url=old_user.avatar_url
                    )
                )
                
                await dbsession.commit()
                return True
            except NotFound:
                raise NotFound("Recovery failed, user or recovery code not found")

    async def revoke_refresh_session(self, fingerprint: str, revoked: bool = True):
        async with self.async_session() as dbsession:
            await dbsession.execute(
                update(RefreshSession)
                .values(revoked=revoked)
                .where(RefreshSession.fingerprint == fingerprint)
            )
            await dbsession.commit()
            return True

    async def clear_db(self):
        async with self.async_session() as dbsession:
            await dbsession.execute(
                delete(RefreshSession).where(or_(
                    RefreshSession.revoked == True,
                    RefreshSession.used_at
                    <= (
                        datetime.now() - parse_expire(str(os.getenv("REFRESH_EXPIRE")))
                    ))
                )
            )
            await dbsession.execute(
                delete(OneTimeCode).where(or_(
                    OneTimeCode.accepted == True,
                    OneTimeCode.created_at
                    <= (datetime.now() - parse_expire(str(os.getenv("LOGIN_EXPIRE")))),
                ))
            )
            await dbsession.commit()

    async def seed_admin_key(self) -> None:
        raw_key = os.getenv("API_TOKEN_HASH", "")
        if not raw_key or not raw_key.startswith("sk_"):
            return

        key_hash = create_hash("API_SECRET", raw_key)

        async with self.async_session() as dbsession:
            result = await dbsession.execute(
                select(ApiKey).where(ApiKey.api_key_hash == key_hash)
            )
            if result.scalar_one_or_none():
                return

            result = await dbsession.execute(
                select(User).where(User.telegram_id == 0)
            )
            bot_user = result.scalar_one_or_none()

            if not bot_user:
                result = await dbsession.execute(
                    insert(User)
                    .values(
                        telegram_id=0,
                        username="system_bot",
                        name="System Bot",
                        role="admin",
                        avatar_url="",
                        last_seen=datetime.now(),
                    )
                    .returning(User)
                )
                bot_user = result.scalar_one()
                await dbsession.flush()

            await dbsession.execute(
                insert(ApiKey).values(
                    user_id=bot_user.id,
                    name="Admin Bot Key",
                    api_key_hash=key_hash,
                )
            )
            await dbsession.commit()

    async def create_db(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()


db_client = Database()
