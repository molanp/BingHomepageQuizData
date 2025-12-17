let currentQuizIndex = 0;
let correctQuizCount = 0;
let quizList = [];

// 鼓励文案列表
const encouragementMessages = [
    ["继续努力呀！"],  // 0 题目答对
    ["继续努力呀！"],  // 1 题目答对
    ["还不错哦！"],  // 2 题目答对
    ["太赞啦！"]  // 3 及以上题目答对
];

function renderQuiz(quizData) {
    quizList = quizData.result;
    renderCurrentQuiz();
}

function renderCurrentQuiz() {
    const container = document.getElementById("quizContainer");
    container.innerHTML = "";

    if (currentQuizIndex >= quizList.length) {
        renderScorePage();
        return;
    }

    const q = quizList[currentQuizIndex];
    const totalVotes = Object.values(q.choices).reduce((a, b) => a + b, 0);
    const block = document.createElement("div");
    block.className = "quiz-block";

    const title = document.createElement("h3");
    title.textContent = `Q${currentQuizIndex + 1}: ${q.question}`;
    block.appendChild(title);

    Object.entries(q.choices).forEach(([choice, count]) => {
        const btn = document.createElement("button");
        btn.className = "option-btn";
        btn.innerHTML = `<span>${choice}</span>`;
        btn.dataset.choice = choice;
        block.appendChild(btn);
    });

    container.appendChild(block);

    const buttons = block.querySelectorAll(".option-btn");
    buttons.forEach((btn) => {
        btn.onclick = () => {
            const selected = btn.dataset.choice;
            const correct = selected === q.answer;
            if (correct) {
                correctQuizCount++;
            }
            disableOtherButtons(block);

            buttons.forEach((b) => {
                const { choice } = b.dataset;
                const count = q.choices[choice];
                const percent = ((count / totalVotes) * 100).toFixed(1);
                const isCorrect = choice === q.answer;
                const isSelected = choice === selected;

                b.classList.add(isCorrect ? "correct" : "incorrect");
                b.innerHTML = `
                    <span>${choice} ${isCorrect ? "✅" : isSelected ? "❌" : ""}</span>
                    <span class="percent-label">${percent}%</span>
                    <div class="progress-bar">
                      <div class="progress-fill" style="width: ${percent}%"></div>
                    </div>
                  `;
            });

            showAnswer(q.answer, block);
            currentQuizIndex++; // 增加索引以加载下一个题目
            renderNextButton();
        };
    });
}

function renderNextButton() {
    const container = document.getElementById("quizContainer");
    const nextButton = document.createElement("button");
    nextButton.className = "next-btn";
    nextButton.textContent = currentQuizIndex < quizList.length ? "下一题" : "查看得分";
    nextButton.onclick = () => {
        if (currentQuizIndex < quizList.length) {
            renderCurrentQuiz();
        } else {
            renderScorePage();
        }
    };
    container.appendChild(nextButton);
}

function renderScorePage() {
    const container = document.getElementById("quizContainer");
    container.innerHTML = "";

    // 根据答对的题目数量选择鼓励文案
    let encouragementMessage;
    if (correctQuizCount === 0) {
        encouragementMessage = encouragementMessages[0][Math.floor(Math.random() * encouragementMessages[0].length)];
    } else if (correctQuizCount === 1) {
        encouragementMessage = encouragementMessages[1][Math.floor(Math.random() * encouragementMessages[1].length)];
    } else if (correctQuizCount === 2) {
        encouragementMessage = encouragementMessages[2][Math.floor(Math.random() * encouragementMessages[2].length)];
    } else {
        encouragementMessage = encouragementMessages[3][Math.floor(Math.random() * encouragementMessages[3].length)];
    }
    const scoreInfo = document.createElement("p");
    scoreInfo.className = "score-info";
    const sumTtl0 = document.createElement("div");
    sumTtl0.className = "sumTtl";
    sumTtl0.textContent = encouragementMessage;
    const sumTtl1 = document.createElement("div");
    sumTtl1.className = "sumTtl";
    sumTtl1.textContent = `你答对了 ${quizList.length} 个中的 ${correctQuizCount} 个`;
    scoreInfo.appendChild(sumTtl0);
    scoreInfo.appendChild(sumTtl1);
    container.appendChild(scoreInfo);
}

function showAnswer(answer, parent) {
    const info = document.createElement("p");
    info.className = "answer-info";
    info.textContent = `✔ 正确答案：${answer}`;
    parent.appendChild(info);
}

function disableOtherButtons(block) {
    const buttons = block.querySelectorAll("button");
    buttons.forEach((btn) => {
        btn.disabled = true;
        btn.style.opacity = 0.9;
    });
}

// 通用 API 调用
async function callApi(url, targetId) {
    try {
        const res = await fetch(url);
        const data = await res.json();
        const formatted = JSON.stringify(data, null, 2);
        const codeBlock = document.getElementById(targetId);
        codeBlock.textContent = formatted;
        Prism.highlightElement(codeBlock);
    } catch (e) {
        document.getElementById(targetId).textContent = "请求失败：" + e;
    }
}

// 索引缓存与日期范围设置
let indexCache = null;

async function ensureIndexLoaded() {
    if (indexCache) return indexCache;

    const res = await fetch("/history/index.json");
    const index = await res.json();
    indexCache = index.data;

    const dates = Object.keys(indexCache).sort();
    const dateInput = document.getElementById("dateInput");
    dateInput.min = dates[0];
    dateInput.max = dates[dates.length - 1];

    return indexCache;
}

// 查询指定日期题目
async function callDateApi() {
    const date = document.getElementById("dateInput").value.replace(/-/g, "/");
    if (!date) return alert("请选择日期");

    const index = await ensureIndexLoaded();

    if (!index[date]) {
        alert("该日期没有题目数据，请选择有效日期");
        return;
    }

    callApi(index[date], "dateResult");
}

function getLocalDateString() {
    const now = new Date();
    const offset = now.getTimezoneOffset(); // 分钟
    const local = new Date(now.getTime() - offset * 60000);
    return local.toISOString().slice(0, 10);
}

async function loadQuizUnified() {
    const input = document.getElementById("quizDateInput");
    const date = input.value.replace(/-/g, "/");

    const index = await ensureIndexLoaded();
    if (!index[date]) {
        alert("该日期没有题目数据，请选择有效日期");
        return;
    }

    const url = index[date];
    try {
        const res = await fetch(url);
        const data = await res.json();
        currentQuizIndex = 0;
        correctQuizCount = 0;
        renderQuiz(data);
    } catch (err) {
        document.getElementById("quizContainer").textContent = "题目加载失败：" + err;
    }
}

document.getElementById("quizDateInput").value = getLocalDateString();
document.getElementById("dateInput").value = getLocalDateString();
