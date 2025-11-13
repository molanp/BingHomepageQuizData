import json
import requests
from pathlib import Path
from collections import defaultdict
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from utils import get_yesterday_date, read_json, write_json, log

# 📁 路径配置
ROOT = Path(__file__).parent.parent
HISTORY = ROOT / "history"
SITEMAPS = ROOT / "sitemaps"
INDEX_PATH = ROOT / "index.json"
BASE_URL = "https://bing.awkchan.top"  # ← 替换为你的域名

# 📂 自动创建目录
for folder in [HISTORY, SITEMAPS]:
    folder.mkdir(parents=True, exist_ok=True)

# 📅 获取昨天日期
date = get_yesterday_date()
log(f"📅 正在更新 {date} 的 quiz 记录...")

# 📄 读取昨天的 quiz 数据
data_path = HISTORY / f"{date}.json"
data = read_json(data_path)
result = []

# 🔄 更新每道题的投票数据
for idx, r in enumerate(data.get("result", [])):
    log(f"🔄 正在更新第 {idx} 题: {r['question']}")
    try:
        response = requests.post(
            "https://www.bing.com/funapi/api/quiz/record",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"QuestionText": r["question"]}),
        )
        r["choices"] = response.json().get("TotalQuestionVotesCount", {})
        result.append(r)
        log(f"✅ 成功更新: {r['question']}")
    except Exception as e:
        log(f"❌ 更新失败: {r['question']} - {type(e).__name__}: {e}")
        result.append(r)

# 💾 写回更新后的数据
data["result"] = result
write_json(data_path, data)
log(f"📁 已写入更新后的数据到 {data_path.name}")

# 🌐 读取 index.json（只读）
index_data = read_json(INDEX_PATH)
yearly = defaultdict(dict)
for d, p in index_data["data"].items():
    year = d[:4]
    yearly[year][d] = p

# 🗂️ 生成年度 sitemap 文件
for year, entries in yearly.items():
    urlset = Element('urlset', {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
    for d, p in sorted(entries.items()):
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = f"{BASE_URL}{p}"
        SubElement(url, 'lastmod').text = d
        SubElement(url, 'changefreq').text = 'never'
        SubElement(url, 'priority').text = '0.8'
    xml = parseString(tostring(urlset)).toprettyxml(indent="  ", encoding="utf-8")
    with open(SITEMAPS / f"sitemap-{year}.xml", 'wb') as f:
        f.write(xml)
    log(f"🗂️ 已更新 sitemap-{year}.xml")

# 📦 生成 sitemap-index.xml
sitemap_index = Element('sitemapindex', {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
for year in sorted(yearly.keys()):
    sitemap = SubElement(sitemap_index, 'sitemap')
    SubElement(sitemap, 'loc').text = f"{BASE_URL}/sitemaps/sitemap-{year}.xml"
    SubElement(sitemap, 'lastmod').text = max(yearly[year].keys())
index_xml = parseString(tostring(sitemap_index)).toprettyxml(indent="  ", encoding="utf-8")
with open(SITEMAPS / "sitemap-index.xml", 'wb') as f:
    f.write(index_xml)
log("📦 已更新 sitemap-index.xml")