import hashlib
import hmac
import os
import random
import re
import string
from datetime import UTC, datetime, timedelta

from user_agents import parse


def parse_expire(date: str) -> timedelta:
    match = re.match(r"(\d+)([smhd])", date)
    if not match:
        raise ValueError(f"Invalid expire format: {date}")
    val, unit = match.groups()
    val = int(val)
    if unit == "s":
        return timedelta(seconds=val)
    elif unit == "m":
        return timedelta(minutes=val)
    elif unit == "h":
        return timedelta(hours=val)
    elif unit == "d":
        return timedelta(days=val)
    else:
        raise ValueError(f"Unknown unit: {unit}")


def is_date_expired(created, expire_delta: str) -> bool:
    return datetime.now() > created + parse_expire(expire_delta)



def create_hash(key: str | bytes, msg: str, from_env: bool = True, hex: bool = True) -> str | bytes:
    if isinstance(key, str):
        k = str(os.getenv(key)).encode() if from_env else key.encode()
    else:
        k = key

    h = hmac.new(k, msg.encode(), hashlib.sha256)
    return h.hexdigest() if hex else h.digest()


def gen_code(length=16):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def parse_user_agent_data(user_agent_string: str) -> dict:
    if not user_agent_string:
        return {
            "device": "Unknown",
            "system": "Unknown",
            "browser": "Unknown"
        }

    user_agent = parse(user_agent_string)

    device_type = ""
    if user_agent.is_mobile:
        device_type = "Mobile"
    elif user_agent.is_tablet:
        device_type = "Tablet"
    elif user_agent.is_pc:
        device_type = "PC"
    elif user_agent.is_bot:
        device_type = "Bot/Spider"
    else:
        device_type = "Other"

    device_name = user_agent.device.model or device_type

    system_info = f"{user_agent.os.family} {user_agent.os.version_string}"

    browser_info = f"{user_agent.browser.family} {user_agent.browser.version_string}"

    return {
        "dev": device_name,
        "system": system_info,
        "browser": browser_info
    }