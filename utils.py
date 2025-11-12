from pathlib import Path
from datetime import datetime, timedelta
import pytz  # pyright: ignore[reportMissingModuleSource]
import json
import sys
import logging

# 初始化 logger
_logger = logging.getLogger("quiz_logger")
_logger.setLevel(logging.INFO)

if not _logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.stream.reconfigure(encoding="utf-8")
    formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

# 设置时区为北京时间
logging.Formatter.converter = lambda *args: datetime.now(pytz.timezone("Asia/Shanghai")).timetuple()

def log(*args, sep=" "):
    message = sep.join(str(arg) for arg in args)
    _logger.info(message)


def read_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def write_json(file_path: Path, data: dict):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_current_date():
    beijing_tz = pytz.timezone("Asia/Shanghai")
    beijing_time = datetime.now(beijing_tz)
    return beijing_time.strftime("%Y-%m-%d")


def get_yesterday_date():
    beijing_tz = pytz.timezone("Asia/Shanghai")
    beijing_time = datetime.now(beijing_tz) - timedelta(days=1)
    return beijing_time.strftime("%Y-%m-%d")
