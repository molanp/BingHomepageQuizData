from pathlib import Path
import random
import time
from quiz import fetch_quiz_results
from utils import read_json, write_json, get_current_date, log


PATH = Path(__file__).parent.parent
OK = False
retry = 0


while not OK:
    sleep_time = random.randint(5, 20)
    log(f"🕒 随机睡眠 {sleep_time}s...")
    time.sleep(sleep_time)

    try:
        log(f"🔄 第 {retry} 次尝试抓取 quiz 结果...")
        results = fetch_quiz_results()
        today = get_current_date()
        data = {
            "$schema": "https://raw.githubusercontent.com/molanp/BingHomepageQuizData/refs/heads/main/schema.json",
            "date": today,
            "result": results,
        }

        log("📦 保存结果到 current.json")
        write_json(PATH / "current.json", data)

        log(f"📦 保存结果到 history/{today}.json")
        write_json(PATH / "history" / f"{today}.json", data)

        log("🗂️ 更新历史索引文件 index.json")
        data_list = read_json(PATH / "history" / "index.json")
        data_list["time"] = time.time()
        data_list["data"][today] = f"/history/{today}.json"
        write_json(PATH / "history" / "index.json", data_list)

        log(f"✅ 抓取成功，共 {len(results)} 题，已写入历史记录")
        OK = True

    except Exception as e:
        log(f"❌ 第 {retry} 次失败: {type(e).__name__} - {e}")
        if retry >= 2:
            log("🚫 Quiz 抓取失败，已达到最大重试次数")
            raise e
        retry += 1
        backoff = random.randint(5, 30)
        log(f"⏳ 等待 {backoff}s 后重试...")
        time.sleep(backoff)
