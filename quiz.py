import json
import os
import re
import time
from urllib.parse import urljoin
import requests
import contextlib
from pathlib import Path
from DrissionPage import ChromiumOptions, ChromiumPage
from utils import log

# 设置浏览器路径
localappdata = os.path.expandvars("%LOCALAPPDATA%")
tree = Path(localappdata) / "ms-playwright/"
chromium_dirs = list(tree.glob("chromium-*"))
co = ChromiumOptions()
co.set_browser_path(chromium_dirs[0] / "chrome-win" / "chrome.exe")


def fetch_quiz_results(max_retries=3):
    page = ChromiumPage(co)
    page.get(
        "https://www.bing.com/search?q=bing+homepage+quiz&form=ML2BF1&OCID=ML2BF1&mkt=zh-CN"
    )

    answers = []
    for i in range(3):  # 固定处理三道题
        for attempt in range(1, max_retries + 1):
            try:
                result, page = get_quiz(page, i)
                answers.append(result)
                break
            except Exception as e:
                log(f"⚠️ [Retry {attempt}/{max_retries}] 第{i}题失败: {e}")

                if attempt == max_retries:
                    log(f"❌ [Skipped] 第{i}题重试失败，跳过。")

    page.close()
    return answers


def get_quiz(page: ChromiumPage, i: int):
    log(f"\n🟩========== 开始处理第 {i} 题 ==========")
    log(f"🌐 当前页面 URL: {page.url}")

    if theme2 := page.ele(".btq_main"):
        log("✅ [HTML模式] 找到主题2页面结构，使用 JS 模式解析。")
        log("📄 [页面结构预览] .btq_main HTML:")
        log(theme2.inner_html)

    if match := re.search(
        r"var\s+RequeryURLChoice\s*=\s*(\{.*?\});", page.html, re.DOTALL
    ):
        json_str = match[1].replace("\u0026", "&")
        data = json.loads(json_str)
        urls = data.get("ChoiceUrls", [])
        log("🧪 [JS解析选项链接准备] ChoiceUrls:", urls)
        url = urljoin(page.url, urls[0])
        log(f"🖱️ [JS解析选项链接] 获取到第一个选项链接: {url}")
        # page.get(urls)

    question = None
    answer = None

    try:
        log("🔍 [HTML模式] 尝试提取题目...")
        question = page.ele(f"#wk_question_text{i}").text
        log(f"📝 [HTML模式] 题目: {question}")

        url = page.ele(".wk_choicesInstLink").link
        page.get(url)
        log(f"🖱️ [解析链接] 获取到第一个选项链接: {url}")

        answer_raw = page.ele(f"#ActualCorrectAnswer{i}").text
        assert isinstance(answer_raw, str)
        log(f"📦 [HTML模式] 原始答案文本: {answer_raw}")

        match = re.search(r"(.+?)\s*(\d+%)", answer_raw)
        answer = match[1] if match else answer_raw
        log(f"✅ [HTML模式] 正确答案: {answer}")

    except Exception as e:
        log(f"⚠️ [HTML模式] 提取失败: {e}")
        log("🔁 [JS fallback] 尝试使用 JS 初始化结构提取...")

        raw = page.html

        pattern = re.compile(
            r'var\s+choices\s*=\s*(\[[^\]]+\]);\s*QuizQuestionPane\.init\(\s*"{}"\s*,\s*"[^"]+"\s*,\s*"([^"]+)"\s*,\s*choices'.format(
                i
            ),
            re.DOTALL,
        )
        match = pattern.search(raw)
        if not match:
            raise ValueError(f"❌ [JS fallback] 未找到第{i}题的结构化数据")

        choices_js_str, question = match.groups()
        log(f"📝 [JS fallback] 题目: {question}")
        log(f"📦 [JS fallback] 原始 choices 字符串:\n{choices_js_str}")

        def js_object_to_json(js_text: str) -> str:
            js_text = js_text.strip().rstrip(";")
            js_text = re.sub(r"(\s*)(\w+):", r'\1"\2":', js_text)
            return js_text

        choices_json_str = js_object_to_json(choices_js_str)
        log(f"🔧 [JS fallback] 转换后的 JSON 字符串:\n{choices_json_str}")

        try:
            choices_data = json.loads(choices_json_str)
        except Exception as e:
            raise ValueError(f"❌ [JS fallback] JSON解析失败: {e}")

        answer = next(
            (c["text"] for c in choices_data if c["isCorrect"] == "true"), None
        )

        log(f"✅ [JS fallback] 正确答案: {answer}")
        log("🖱️ [解析链接] 尝试获取第一个选项链接并跳转...")
        url = page.ele(".acf-button-standard__link").link
        page.get(url)
        log(f"🖱️ [解析链接] 获取到第一个选项链接: {url}")
    log("📊 [选项投票统计] 请求 funapi 接口...")

    record = requests.post(
        "https://www.bing.com/funapi/api/quiz/record",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"QuestionText": question}),
    )
    choices = record.json().get("TotalQuestionVotesCount", {})
    log(f"📊 [选项投票统计] 返回结果: {choices}")

    log(f"\n🧾 [题目结构预览] 第{i}题")
    log(f"📝 题目: {question}")
    log(f"✅ 正确答案: {answer}")
    log(f"📊 投票统计: {choices}")

    with contextlib.suppress(Exception):
        if i < 2:
            log("⏭️ [跳转下一题] 尝试点击下一题按钮...")

            time.sleep(2)
            try:
                page.ele(f"#nextQuestionbtn{i}").click()
            except Exception:
                try:
                    page.ele("tag:button@title=下一个").click()
                except Exception:
                    page.ele("Next Question").click()
            log("⏭️ [跳转下一题] 已进入下一题")

    log(f"🟥========== 结束处理第 {i} 题 ==========\n")

    return {
        "question": question,
        "answer": answer,
        "choices": choices,
    }, page
