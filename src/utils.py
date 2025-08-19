from pathlib import Path
from datetime import datetime
import pytz # pyright: ignore[reportMissingModuleSource]
import json


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
    # 创建北京时间时区对象
    beijing_tz = pytz.timezone("Asia/Shanghai")
    # 获取当前北京时间
    beijing_time = datetime.now(beijing_tz)
    return beijing_time.strftime("%Y-%m-%d")
