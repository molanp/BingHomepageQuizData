from pathlib import Path
import random
import time
from quiz import fetch_quiz_results
from utils import read_json, write_json, get_current_date
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
PATH = Path(__file__).parent.parent
OK = False
retry = 0

while not OK:
    s = random.randint(5, 20)
    print(f"随机睡眠 {s}s....")
    sys.stdout.flush()
    time.sleep(s)
    try:
        print(f"{retry}:Fetching quiz results...")
        sys.stdout.flush()
        results = fetch_quiz_results()
        today = get_current_date()
        data = {"date": today, "result": results}
        write_json(PATH / "current.json", data)
        print("Saved to current.json")
        sys.stdout.flush()
        write_json(PATH / "history" / f"{today}.json", data)
        print(f"Saved to history/{today}.json")
        sys.stdout.flush()
        data_list = read_json(PATH / "history" / "index.json")
        data_list["time"] = time.time()
        data_list["data"][today] = f"/history/{today}.json"
        write_json(PATH / "history" / "index.json", data_list)
        print("Successfully update history/index.json")
        sys.stdout.flush()
        OK = True
    except Exception as e:
        if retry >= 5:
            print("Quiz failed")
            sys.stdout.flush()
            raise e
        print(f"{retry} Fail: {type(e)} {e}")
        sys.stdout.flush()
        retry += 1
        time.sleep(random.randint(5, 30))
