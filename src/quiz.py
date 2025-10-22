import contextlib
import json
import os
from pathlib import Path
import sys
from DrissionPage import ChromiumOptions, ChromiumPage
import re
import time
import requests

localappdata = os.path.expandvars("%LOCALAPPDATA%")
tree = Path(localappdata) / "ms-playwright/"
chromium_dirs = list(tree.glob("chromium-*"))
co = ChromiumOptions()
co.set_browser_path(chromium_dirs[0] / "chrome-win" / "chrome.exe")


def fetch_quiz_results():

    page = ChromiumPage(co)
    page.get(
        "https://www.bing.com/search?q=bing+homepage+quiz&form=ML2BF1&OCID=ML2BF1&mkt=zh-CN"
    )
    print("Current URL: ", page.url)
    sys.stdout.flush()
    answers = []
    for i in range(3):
        try:
            d = get_quiz(page, i)
        except Exception as e:
            print(page.html)
            sys.stdout.flush()
            raise e
        answers.append(d[0])
        page = d[1]
    page.close()
    return answers


# TODO Rename this here and in `fetch_quiz_results`
def get_quiz(page: ChromiumPage, i: int):
    try:
        question = page.ele(f"#wk_question_text{i}").text
    except:
        question = page.ele(".btq_quesLrge").text
    print("Sucessfully fetched question")
    sys.stdout.flush()
    record = requests.post(
        "https://www.bing.com/funapi/api/quiz/record",
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "QuestionText": question,
            }
        ),
    )
    choices = record.json()["TotalQuestionVotesCount"]
    print(f"Successful to get choices, preview: {choices}")
    sys.stdout.flush()
    with contextlib.suppress(RuntimeError):
        t = page.ele(f"#questionOptionChoice{i}0").click.for_new_tab()  # type: ignore
        page.get(t.url)
        t.close()
    if e := page.ele(".wk_correctAns"):
        right = e.text
        rep = re.search(r"(.+?)\s*(\d+%)", right)  # type: ignore
        assert rep
        answer = rep[1]
    else:
        answer = page.ele(".wk_choiceMaxWidthAns").text

    print(f"-----------------Topic {i}-----------------")
    print("Question:", question)
    print("Choices:", choices)
    print("Answer:", answer)
    sys.stdout.flush()
    if i < 2:
        time.sleep(0.5)
        page.ele(f"#nextQuestionbtn{i}").click()
    return {
        "question": question,
        "answer": answer,
        "choices": choices,
    }, page
