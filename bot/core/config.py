import logging
import sys
from typing import List

from loguru import logger
from starlette.config import Config

config = Config(".env")

DEBUG: bool = config("DEBUG", cast=bool, default=False)

if DEBUG:
    TOKEN: str = config("TOKEN_TEST", cast=str)
    CHAT_ID: str = config("CHAT_ID_TEST", cast=str)
    REDIS_HOST: str = config("REDIS_HOST_TEST", cast=str, default='127.0.0.1')
else:
    TOKEN: str = config("TOKEN", cast=str)
    CHAT_ID: str = config("CHAT_ID", cast=str)
    REDIS_HOST: str = config("REDIS_HOST", cast=str, default='redis')

ACL: List[str] = config("ACL")

REDIS_PASS: str = config("REDIS_PASS", cast=str)
REDIS_DB_FOR_BOT_STATE: int = config("REDIS_DB_FOR_BOT_STATE", cast=int, default=1)
REDIS_DB_FOR_BOT_DATA: int = config("REDIS_DB_FOR_BOT_DATA", cast=int, default=0)

JOIN_LINK: str = config("JOIN_LINK", cast=str, default='https://t.me/')
JOIN_TEXT: str = config("JOIN_TEXT", cast=str, default='JoinText')

# logging configuration

LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=LOGGING_LEVEL)

logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
