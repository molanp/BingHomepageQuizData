import json
import requests
from pathlib import Path
from utils import get_yesterday_date, read_json, write_json, log


# 路径与日期
PATH = Path(__file__).parent.parent
date = get_yesterday_date()
log(f"📅 正在更新 {date} 的 quiz 记录...")

# 读取历史数据
data_path = PATH / "history" / f"{date}.json"
data = read_json(data_path)
result = []

# 更新每道题的投票数据
for idx, r in enumerate(data.get("result", [])):
    log(f"🔄 正在更新第 {idx} 题: {r['question']}")
    try:
        response = requests.post(
            "https://www.bing.com/funapi/api/quiz/record",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"QuestionText": r["question"]}),
        )
        r["choices"] = response.json().get("TotalQuestionVotesCount", {})
        result.append(r)
        log(f"✅ 成功更新: {r['question']}")
    except Exception as e:
        log(f"❌ 更新失败: {r['question']} - {type(e).__name__}: {e}")
        result.append(r)  # 保留原始数据，避免丢失

# 写回文件
data["result"] = result
write_json(data_path, data)
log(f"📁 已写入更新后的数据到 {data_path.name}")
