from pathlib import Path
from quiz import fetch_quiz_results
from utils import write_json, get_current_date

PATH = Path(__file__).parent.parent


def main():
    results = fetch_quiz_results()
    today = get_current_date()
    data = {"date": today, "result": results}
    write_json(PATH / "current.json", data)
    write_json(PATH / "history" / f"{today}.json", data)


if __name__ == "__main__":
    main()
