import logging
import os
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler


@dataclass
class Colors:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BOLD = "\033[1m"
    RESET = "\033[0m"


class ConsoleFormatter(logging.Formatter):
    def format(self, record):
        lvl = record.levelname  # оригинал
        colored = lvl
        if lvl == "INFO":
            colored = f"{Colors.BOLD}{Colors.GREEN}[I]{Colors.RESET}"
        elif lvl == "WARNING":
            colored = f"{Colors.BOLD}{Colors.YELLOW}[W]{Colors.RESET}"
        elif lvl == "DEBUG":
            colored = f"{Colors.BOLD}{Colors.BLUE}[D]{Colors.RESET}"
        elif lvl == "ERROR":
            colored = f"{Colors.BOLD}{Colors.RED}[E]{Colors.RESET}"

        # Временно подменим для вывода
        record.levelname = colored
        out = super().format(record)
        record.levelname = lvl  # восстановим оригинал
        return out


class FileFormatter(logging.Formatter):
    def format(self, record):
        lvl = record.levelname
        short = lvl
        if lvl == "INFO":
            short = "[I]"
        elif lvl == "WARNING":
            short = "[W]"
        elif lvl == "DEBUG":
            short = "[D]"
        elif lvl == "ERROR":
            short = "[E]"

        record.levelname = short
        out = super().format(record)
        record.levelname = lvl
        return out


def setup_logger() -> logging.Logger:
    logger_new = logging.getLogger("aiogram_bot")
    logger_new.setLevel(logging.DEBUG)

    console_formatter = ConsoleFormatter(
        "%(levelname)s " + Colors.WHITE + "%(message)s" + Colors.RESET
    )

    fileformatter = FileFormatter(
        "%(levelname)s [%(filename)s:%(lineno)-3d] %(message)s"
    )

    log_path = os.path.join("logs", "app.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    fh = RotatingFileHandler(
        log_path, maxBytes=10_000_000, backupCount=5, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fileformatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(console_formatter)

    logger_new.addHandler(fh)
    logger_new.addHandler(ch)

    return logger_new


logger = setup_logger()
