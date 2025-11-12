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
        document.getElementById(targetId).textContent = '请求失败：' + e;
    }
}

// 索引缓存与日期范围设置
let indexCache = null;

async function ensureIndexLoaded() {
    if (indexCache) return indexCache;
    
    const res = await fetch('/history/index.json');
    const index = await res.json();
    indexCache = index.data;
    
    const dates = Object.keys(indexCache).sort();
    const dateInput = document.getElementById('dateInput');
    dateInput.min = dates[0];
    dateInput.max = dates[dates.length - 1];
    
    return indexCache;
}

// 查询指定日期题目
async function callDateApi() {
    const date = document.getElementById('dateInput').value;
    if (!date) return alert('请选择日期');
    
    const index = await ensureIndexLoaded();
    
    if (!index[date]) {
        alert('该日期没有题目数据，请选择有效日期');
        return;
    }
    
    callApi(index[date], 'dateResult');
}

function getLocalDateString() {
    const now = new Date();
    const offset = now.getTimezoneOffset(); // 分钟
    const local = new Date(now.getTime() - offset * 60000);
    return local.toISOString().slice(0, 10);
}
async function loadQuizUnified() {
    const input = document.getElementById('quizDateInput');
    const date = input.value;
    
    const index = await ensureIndexLoaded();
    if (!index[date]) {
        alert('该日期没有题目数据，请选择有效日期');
        return;
    }
    
    const url = index[date];
    try {
        const res = await fetch(url);
        const data = await res.json();
        renderQuiz(data.result);
    } catch (err) {
        document.getElementById('quizContainer').textContent = '题目加载失败：' + err;
    }
}
// 渲染答题卡片
function renderQuiz(quizList) {
    const container = document.getElementById('quizContainer');
    container.innerHTML = '';
    
    quizList.forEach((q, index) => {
        const totalVotes = Object.values(q.choices).reduce((a, b) => a + b, 0);
        const block = document.createElement('div');
        block.className = 'quiz-block';
        
        const title = document.createElement('h3');
        title.textContent = `Q${index + 1}: ${q.question}`;
        block.appendChild(title);
        
        Object.entries(q.choices).forEach(([choice, count]) => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.innerHTML = `<span>${choice}</span>`;
            btn.dataset.choice = choice;
            block.appendChild(btn);
        });
        
        container.appendChild(block);
        
        const buttons = block.querySelectorAll('.option-btn');
        buttons.forEach(btn => {
            btn.onclick = () => {
                const selected = btn.dataset.choice;
                const correct = selected === q.answer;
                disableOtherButtons(block);
                
                buttons.forEach(b => {
                    const {choice} = b.dataset;
                    const count = q.choices[choice];
                    const percent = ((count / totalVotes) * 100).toFixed(1);
                    const isCorrect = choice === q.answer;
                    const isSelected = choice === selected;
                    
                    b.classList.add(isCorrect ? 'correct' : 'incorrect');
                    b.innerHTML = `
            <span>${choice} ${isCorrect ? '✅' : isSelected ? '❌' : ''}</span>
            <span class="percent-label">${percent}%</span>
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${percent}%"></div>
            </div>
          `;
                });
                
                showAnswer(q.answer, block);
            };
        });
    });
}

// 显示正确答案
function showAnswer(answer, parent) {
    const info = document.createElement('p');
    info.className = 'answer-info';
    info.textContent = `✔ 正确答案：${answer}`;
    parent.appendChild(info);
}

// 禁用所有按钮
function disableOtherButtons(block) {
    const buttons = block.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = 0.9;
    });
}

document.getElementById('quizDateInput').value = getLocalDateString();
document.getElementById('dateInput').value = getLocalDateString();