from telebot import TeleBot
from telebot.types import Message

from modules import bot

import importlib
import os
import time
from concurrent.futures import ThreadPoolExecutor

from pocketbase.models import Record
from modules.db import dbclient, PocketBaseClient
from modules.logging import logger

class TranslationManager:
    def __init__(self):
        self.client = dbclient
        self.cash = {}
        self.cash_translations()

    def cash_translations(self):
        self.cash = self.client.get_all_translations()

    def t(self, message: Message, key:str):
        lang = self.client.get_lang(message)
        keylist = key.split('/')

        lang_data = self.cash.get(lang).get('data')
        if not lang_data:
            return "LangNotFound"

        result = None

        for key in keylist:
            result = lang_data.get(key, None)

            if result is None:
                raise Exception(f"key {key} not found")

        if not result:
            return "MsgNotFound"

        logger.debug(f"Translation {lang} -> {"".join(result.get('msg')).replace('\n', ' ')[:15]}...")
        return result


translations = TranslationManager()


class BasePlugin:
    def __init__(self):
        self.bot: TeleBot = bot
        self.db_client: PocketBaseClient = dbclient
        self.translations: TranslationManager = translations

        self.chat_id: int | None = None
        self.user_id: int | None = None


class MessagePlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.msg = None


class CallbackPlugin(MessagePlugin):
    def __init__(self):
        super().__init__()
        self.callback_args: list[str] | None = None
        self.callback_data: str | None = None


class InlinePlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.inline_data = None
        self.text: str | None = None


class CommandPlugin(MessagePlugin):
    def __init__(self):
        super().__init__()
        self.command_text: str | None = None


class Plugin:
    @staticmethod
    def create(plugin_type: str):
        if plugin_type == "message":
            return MessagePlugin()
        elif plugin_type == "callback":
            return CallbackPlugin()
        elif plugin_type == "inline":
            return InlinePlugin()
        elif plugin_type == "command":
            return CommandPlugin()
        raise ValueError(f"Unknown plugin type {plugin_type}")


class PluginManager:
    db_client = dbclient.pb

    def __init__(self):
        self.plug_dir = os.path.join(os.getcwd(), 'plugins')
        self.loaded_modules: dict[str, object] = {}

        # handlers maps
        self.command_map: dict[str, dict] = {}
        self.inline_map: dict[str, dict] = {}
        self.callback_patterns: list[dict] = []  # сложные match с ':'
        self.message_map: dict[str, list] = {}

        # thread pool for async execution
        self.executor = ThreadPoolExecutor(max_workers=10)

        self.load()

    def load(self):
        logger.info(f"Loading plugins from {self.plug_dir}")
        self.load_commands()
        self.load_callbacks()
        self.load_inline()
        self.load_messages()

    def _add_command(self, command: str, handler: str, record: Record):
        self.command_map[command] = {
            "target": command,
            "handler": handler,
            "raw": record,
        }

    def _add_callback(self, pattern: str, handler: str, record: Record):
        self.callback_patterns.append({
            "target": pattern,
            "handler": handler,
            "raw": record,
        })

    def _add_inline(self, prefix: str, handler: str, record: Record):
        self.inline_map[prefix] = {
            "target": prefix,
            "handler": handler,
            "raw": record,
        }

    def _add_message(self, mime: str, handler: str, record: Record):
        if mime not in self.message_map:
            self.message_map[mime] = []
        self.message_map[mime].append({
            "mimes": [mime],
            "handler": handler,
            "raw": record,
        })

    def load_commands(self):
        try:
            records = self.db_client.collection('command_handlers').get_full_list()
        except Exception as e:
            logger.error(f"Failed to load command handlers: {e}")
            return

        for record in records:
            if not getattr(record, "enabled", True):
                continue
            commands = getattr(record, "commands", "")
            handler = getattr(record, "plugin", None)
            if not handler:
                continue

            for cmd in [x.strip() for x in commands.split(',') if x.strip()]:
                self._add_command(cmd, handler, record)

    def load_callbacks(self):
        try:
            records = self.db_client.collection('callback_handlers').get_full_list()
        except Exception as e:
            logger.error(f"Failed to load callback handlers: {e}")
            return

        for record in records:
            if not getattr(record, "enabled", True):
                continue
            pattern = getattr(record, "callback_format", None)
            handler = getattr(record, "plugin", None)
            if pattern and handler:
                self._add_callback(pattern, handler, record)

    def load_inline(self):
        try:
            records = self.db_client.collection('inline_handlers').get_full_list()
        except Exception as e:
            logger.error(f"Failed to load inline handlers: {e}")
            return

        for record in records:
            if not getattr(record, "enabled", True):
                continue
            prefix = getattr(record, "query_format", None)
            handler = getattr(record, "plugin", None)
            if prefix and handler:
                self._add_inline(prefix, handler, record)

    def load_messages(self):
        try:
            records = self.db_client.collection('message_handlers').get_full_list()
        except Exception as e:
            logger.error(f"Failed to load message handlers: {e}")
            return

        for record in records:
            if not getattr(record, "enabled", True):
                continue
            content_types = getattr(record, "content_types", "")
            handler = getattr(record, "plugin", None)
            if not handler:
                continue

            for mime in [x.strip() for x in content_types.split(',') if x.strip()]:
                self._add_message(mime, handler, record)

    def _get_module(self, path: str):
        if not path:
            return None
        if path in self.loaded_modules:
            return self.loaded_modules[path]

        normalised = path.replace("/", ".")
        if normalised.endswith(".py"):
            normalised = normalised[:-3]

        try:
            mod = importlib.import_module(normalised)
            self.loaded_modules[path] = mod
            return mod
        except Exception as e:
            logger.error(f"Module load error {path}: {e}")
            return None

    def find_command(self, text: str):
        record = self.command_map.get(text)
        if record:
            yield record

    def find_callback(self, callback_data: str):
        if not callback_data:
            return
        parts = callback_data.split(':')

        for record in self.callback_patterns:
            target = record['target']
            if not target:
                continue

            if target.startswith("command:"):
                cmd_txt = callback_data[len("command:"):]
                yield from self.find_command(cmd_txt)
                continue

            if callback_data.startswith(target):
                yield record
                continue

            tokens = target.split(':')
            if all(
                token == '*' or (i < len(parts) and token == parts[i])
                for i, token in enumerate(tokens)
            ):
                yield record

    def find_inline(self, query: str):
        for prefix, record in self.inline_map.items():
            if query.startswith(prefix):
                yield record

    def find_message_handler(self, message):
        mt = message.content_type
        for record in self.message_map.get(mt, []):
            yield record

    def run_handler(self, record, plug_context, async_exec=True):
        path = record.get("handler")
        if not path:
            return

        module = self._get_module(path)
        if not module:
            logger.error(f"Handler module not found {path}")
            return

        main_func = getattr(module, "main", None)
        if not main_func:
            logger.error(f"Module has no main {path}")
            return

        def _exec():
            start = time.perf_counter()
            try:
                main_func(plug_context)
            except Exception as e:
                logger.error(f"Plugin run err {path}: {e}")
            finally:
                elapsed = time.perf_counter() - start
                logger.debug(f"Handler {path} finished in {elapsed:.3f}s")

        if async_exec:
            self.executor.submit(_exec)
        else:
            _exec()
