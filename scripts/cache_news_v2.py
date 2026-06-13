#!/usr/bin/env python3
"""
v2 新闻缓存：近3天 + 多源去重 + 精简输出
"""
import json, os, sys
from datetime import datetime, timedelta

NEWS_DIR = r"C:\soft\agent\ai-dashboard\data\news"
os.makedirs(NEWS_DIR, exist_ok=True)
CUTOFF = datetime.now() - timedelta(days=3)

def parse_date(date_str):
    """解析各种日期格式"""
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y%m%d"]:
        try:
            return datetime.strptime(date_str[:19] if len(date_str)>=19 else date_str[:10], fmt)
        except:
            continue
    return None

def normalize(news_item, source_label):
    """统一格式"""
    title = news_item.get("新闻标题", news_item.get("title", ""))
    content_raw = news_item.get("新闻内容", news_item.get("内容", news_item.get("content", ""))) or ""
    date_str = news_item.get("发布时间", news_item.get("date", news_item.get("时间", "")))
    source = news_item.get("文章来源", news_item.get("source", news_item.get("来源", "")))
    link = news_item.get("新闻链接", news_item.get("link", news_item.get("链接", "")))

    # 截断过长内容
    content = content_raw[:200] if content_raw else ""

    # 过滤纯资金流/排名/大宗交易等噪音
    skip_kw = ["资金流出榜", "资金流入榜", "特大单净流入", "特大单净流出",
               "融资客净买入金额排名", "主力资金净流入排名", "大宗交易成交明细",
               "融资余额增加", "杠杆资金", "融资融券余额", "解密主力",
               "主力资金净流出", "主力资金净流入", "资金流向日报",
               "融资客看好", "融资净买入", "融资余额", "杠杆资金大手笔",
               "科创板主力资金", "获融资客大手", "股特大单净流入",
               "获杠杆资金净买入", "融资融券余额每日变动",
               "科创板股今日大宗", "今日大宗交易", "大宗交易平台"]
    for kw in skip_kw:
        if kw in title:
            return None

    # 过滤纯行情统计类标题
    if title.startswith(("电子行业", "计算机行业", "科创板", "6月", "5月", "4月")) and \
       any(x in title for x in ["资金流", "主力", "特大单", "融资", "杠杆"]):
        return None

    # 过滤无关的全局搜索噪音
    if source_label == "Search" and "周刊提前读" in title:
        return None

    dt = parse_date(date_str) if date_str else None
    if not dt or dt < CUTOFF:
        return None

    return {
        "title": title,
        "content": content,
        "date": date_str[:16] if date_str else "",
        "source": f"{source_label}·{source}" if source else source_label,
        "link": link,
        "ts": dt.timestamp(),
    }

def interpret(title, content):
    """一句话解读"""
    t = (title + content)[:200]
    if "H股" in t and "上市" in t: return "筹划港股上市→拓宽融资渠道"
    if "减持" in t: return "减持→短期偏空，关注量级"
    if ("一季报" in t or "年报" in t) and "增长" in t: return "业绩增长→基本面向好"
    if "一季报" in t or "年报" in t: return "财报已出→关注趋势"
    if "涨停" in t or "大涨" in t: return "资金追捧→关注基本面支撑"
    if "跳水" in t or "大跌" in t: return "短期回调→关注量能"
    if "中标" in t or "订单" in t: return "新单落地→利好营收"
    if "成立" in t and "公司" in t: return "新设公司→布局新业务"
    if "发布" in t and "6月15日" in t: return "新品发布在即→关注催化"
    if "上市" in t and "H股" in t: return "赴港上市→国际化布局"
    return ""

def process_batch(sources_data):
    """
    sources_data = [(code, source_label, json_or_list), ...]
    多源合并去重，取近3天
    """
    all_items = []
    seen_titles = set()

    for code, label, raw in sources_data:
        if isinstance(raw, str):
            try: items = json.loads(raw)
            except: continue
        elif isinstance(raw, list):
            items = raw
        else:
            continue

        for item in items:
            norm = normalize(item, label)
            if norm and norm["title"] not in seen_titles:
                seen_titles.add(norm["title"])
                all_items.append(norm)

    # 按时间倒序，取前 8 条
    all_items.sort(key=lambda x: x["ts"], reverse=True)
    top = all_items[:8]

    for item in top:
        item["interpretation"] = interpret(item["title"], item["content"])
        del item["ts"]

    code = sources_data[0][0] if sources_data else "unknown"
    cache = {
        "code": code,
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "count": len(top),
        "items": top,
    }
    filepath = os.path.join(NEWS_DIR, f"{code}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"  {code}: {len(top)} items (from {len(all_items)} raw, filtered ≥{CUTOFF.strftime('%m-%d')})")

if __name__ == "__main__":
    # Expect: python cache_news_v2.py '<json>'
    # json = [[code, label, mcp_result], ...]
    if len(sys.argv) > 1:
        data = json.loads(sys.argv[1])
        process_batch(data)
    print(f"Done. Total cached: {len(os.listdir(NEWS_DIR))}")
