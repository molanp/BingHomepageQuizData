# Bing Homepage Quiz 数据抓取脚本

本分支包含用于自动抓取 Bing Homepage Quiz 数据的 Python 脚本。

## 文件说明

- [main.py](main.py) - 主程序入口，负责整体流程控制和数据存储
- [quiz.py](quiz.py) - 核心抓取逻辑，使用 DrissionPage 抓取题目数据
- [update.py](update.py) - 更新历史数据中的投票统计信息
- [add_schema.py](add_schema.py) - 为历史数据文件添加 JSON Schema 引用
- [utils.py](utils.py) - 工具函数集合，包括文件读写、日期处理和日志功能
- [requirements.txt](requirements.txt) - 项目依赖包列表

## 运行环境

可通过以下命令安装：

```bash
pip install -r requirements.txt
```

## 使用说明

1. 运行 [main.py](main.py) 抓取当日题目数据：

```bash
python main.py
```

2. 运行 [update.py](update.py) 更新昨日题目投票数据：

```bash
python update.py
```

3. 运行 `add_schema.py` 为历史数据添加 schema 引用：

```bash
python add_schema.py
```
