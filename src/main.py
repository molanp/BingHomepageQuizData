from pathlib import Path
from quiz import fetch_quiz_results
from utils import write_json, get_current_date
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
PATH = Path(__file__).parent.parent

print("Fetching quiz results...")
results = fetch_quiz_results()
today = get_current_date()
data = {"date": today, "result": results}
write_json(PATH / "current.json", data)
print("Saved to current.json")
write_json(PATH / "history" / f"{today}.json", data)
print(f"Saved to history/{today}.json")
