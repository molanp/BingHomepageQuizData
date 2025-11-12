from pathlib import Path
from utils import read_json, write_json, log

SCHEMA_URL = "https://raw.githubusercontent.com/molanp/BingHomepageQuizData/refs/heads/main/schema.json"

ROOT = Path(__file__).parent.parent
HISTORY_DIR = ROOT / "history"

def ensure_schema_first(file_path: Path):
    data = read_json(file_path)
    if not isinstance(data, dict) or not data:
        log(f"跳过（非对象或空文件）: {file_path.name}")
        return

    keys = list(data.keys())
    if keys and keys[0] == "$schema" and data["$schema"] == SCHEMA_URL:
        log(f"已存在 schema（跳过）: {file_path.name}")
        return

    # 移除已有的 $schema 再插入到最前面
    data.pop("$schema", None)
    new_data = {"$schema": SCHEMA_URL}
    new_data |= data

    write_json(file_path, new_data)
    log(f"已更新: {file_path.name}")

def main():
    if not HISTORY_DIR.exists():
        log(f"history 目录不存在: {HISTORY_DIR}")
        return

    for p in sorted(HISTORY_DIR.glob("*.json")):
        ensure_schema_first(p)

if __name__ == "__main__":
    main()