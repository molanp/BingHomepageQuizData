import io
import json
from pathlib import Path
import sys
import requests

from utils import get_yesterday_date, read_json, write_json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
PATH = Path(__file__).parent.parent
date = get_yesterday_date()

data = read_json(PATH / "history" / f"{date}.json")

result = []
for r in data["result"]:
    record = requests.post(
        "https://www.bing.com/funapi/api/quiz/record",
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "QuestionText": r["question"],
            }
        ),
    )
    r["choices"] = record.json()["TotalQuestionVotesCount"]
    result.append(r)
    print(f"Successful to update {r['question']} choices")
data["result"] = result
write_json(PATH / "history" / f"{date}.json", data)
