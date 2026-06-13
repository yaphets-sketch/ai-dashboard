#!/usr/bin/env python3
"""缓存个股新闻数据 - 处理 MCP get_stock_news 返回的 JSON"""
import json, os, sys
from datetime import datetime

NEWS_DIR = r"C:\soft\agent\ai-dashboard\data\news"

def save_news(code, raw_json_str):
    """将 MCP get_stock_news 的返回结果存入缓存"""
    try:
        news_list = json.loads(raw_json_str) if isinstance(raw_json_str, str) else raw_json_str
    except:
        news_list = []

    items = []
    for n in news_list[:10]:  # Top 10
        item = {
            "title": n.get("新闻标题", ""),
            "content": n.get("新闻内容", ""),
            "date": n.get("发布时间", ""),
            "source": n.get("文章来源", ""),
            "link": n.get("新闻链接", ""),
        }
        items.append(item)

    cache = {
        "code": code,
        "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "count": len(items),
        "items": items,
    }

    os.makedirs(NEWS_DIR, exist_ok=True)
    filepath = os.path.join(NEWS_DIR, f"{code}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    print(f"Cached {len(items)} news for {code}")
    return cache

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cache_news.py <code> '<json_string>'")
        sys.exit(1)

    code = sys.argv[1]
    raw = sys.argv[2] if len(sys.argv) > 2 else "[]"
    save_news(code, raw)
