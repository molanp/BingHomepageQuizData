from playwright.sync_api import sync_playwright
import re
import time


def fetch_quiz_results():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(locale="zh-CN")
        page = context.new_page()
        page.goto(
            "https://www.bing.com/search?q=Bing%20Homepage%20quiz&form=ML2BF1&OCID=ML2BF1&mkt=zh-CN"
        )
        def handle_page(new_page):
            page.goto(new_page.url)
            new_page.close()
            
        context.on("page", handle_page)
        
        print("Current URL: ", page.url)
        answers = []
        for i in range(3):
            time.sleep(1)
            choices = []
            choices.extend(
                (page.locator(f"#ChoiceText_{i}_{c} > div").first.text_content() or "")
                for c in range(3)
            )
            page.locator(f"#questionOptionChoice{i}1").click()
            question = page.locator(".wk_headingPadding").text_content() or ""
            if page.locator(".wk_correctAns").count() == 1:
                right = page.locator(".wk_correctAns").text_content() or ""
                rep = re.search(r"(.+?)\s*(\d+%)", right)
                assert rep
                answer = rep[1]
                rate = rep[2]
            else:
                answer = page.locator(".wk_choiceMaxWidthAns").text_content() or ""
                rate = page.locator(f"#wk_statistics_{i}_0").text_content() or ""
                rep = re.search(r"(\d+%)", rate)
                assert rep
                rate = rep[1]
            
            print(f"-----------------Topic {i}-----------------")
            print("Question:",question.strip())
            print("Choices:", choices)
            print("Answer:",answer.strip())
            print("Accuracy:",rate)
            answers.append(
                {
                    "question": question.strip(),
                    "answer": answer.strip(),
                    "choices": choices,
                    "rate": rate.strip(),
                }
            )
            time.sleep(1)
            if i < 2:
                page.locator(f"#nextQuestionbtn{i}").click()
        context.close()
        browser.close()
        return answers
