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
    for i in range(2):
        try:
            d = get_quiz(page, i)
        except Exception as e:
            print("###########################")
            print(e)
            print(page.html)
            sys.stdout.flush()
            raise e
        answers.append(d[0])
        page = d[1]
    page.close()
    return answers


# TODO Rename this here and in `fetch_quiz_results`
def get_quiz(page: ChromiumPage, i: int):
    print("Current URL: ", page.url)
    try:
        question = page.ele(f"#wk_question_text{i}").text
    except Exception:
        print("尝试使用第二种方案获取题目内容...")
        sys.stdout.flush()
        raw = page.html
        # 提取问题：QuizQuestionPane.init 的第三个参数是问题文本
        question_match = re.search(
            r'QuizQuestionPane\.init\([^,]+,\s*[^,]+,\s*"([^"]+)"', raw
        )
        question = question_match.group(1) if question_match else None
        # 提取所有选项：从 choices 数组中提取 isCorrect 和 text
        choice_pattern = re.compile(r'isCorrect:\s*"(\w+)",\s*text:\s*"([^"]+)"')
        matches = choice_pattern.findall(raw)

        options = [text for _, text in matches]
        correct_answer = next(
            (text for correct, text in matches if correct == "true"), None
        )

        print(
            "js,extra_preview: ",
            {
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
            },
        )
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
    with contextlib.suppress(Exception):
        try:
            t = page.ele(f"#questionOptionChoice{i}0").click.for_new_tab()  # type: ignore
        except Exception:
            t = page.ele(".btq_opt").click.for_new_tab()  # type: ignore
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
        time.sleep(2)
        try:
            page.ele(f"#nextQuestionbtn{i}").click()
        except Exception:
            page.ele("tag:button@title=下一个").click()
        print("进入下一道题目...")
    return {
        "question": question,
        "answer": answer,
        "choices": choices,
    }, page
