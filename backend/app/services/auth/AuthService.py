import os
from datetime import datetime
from urllib.parse import unquote

import jwt

from app.utils import create_hash, parse_expire


class AuthUtils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def gen_jwt_token(user_id, session_id, role="user", is_bot:bool=False) -> str:
        delta = parse_expire(os.getenv("ACCESS_EXPITRE", "30m"))

        payload = {
            "sub": str(user_id),
            "sid": str(session_id),
            "role": str(role),
            "is_bot": bool(is_bot),
            "exp": datetime.now() + delta
        }
        return jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALG", "HS256"))
    
    @staticmethod
    def check_initdata(initdata:str, hash_str:str, c_str:str = "WebAppData") -> bool:
        bot_token = os.getenv("BOT_TOKEN")
        
        if not bot_token:
            return False

        init_data = sorted([ chunk.split("=") 
        for chunk in unquote(initdata).split("&") 
                if chunk[:len("hash=")]!="hash="],
            key=lambda x: x[0])
        init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])
        
        prehash = create_hash(c_str, bot_token, from_env=False, hex=False)
        new_hash = create_hash(prehash, init_data, from_env=False)
        
        if hash_str != new_hash:
            return False
        
        return True