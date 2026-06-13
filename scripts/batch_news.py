#!/usr/bin/env python3
"""
批量新闻缓存脚本 - 配合 MCP get_stock_news 使用
接收逐批 MCP 返回的新闻 JSON，存入缓存
"""
import json, os, sys

NEWS_DIR = r"C:\soft\agent\ai-dashboard\data\news"
os.makedirs(NEWS_DIR, exist_ok=True)

def save_batch(codes_and_news):
    """
    codes_and_news: list of (code, json_string_from_mcp)
    """
    for code, raw_news in codes_and_news:
        if isinstance(raw_news, str):
            try:
                news_items = json.loads(raw_news)
            except:
                news_items = []
        else:
            news_items = raw_news if isinstance(raw_news, list) else []

        # Clean and normalize
        items = []
        for n in news_items[:8]:
            item = {
                "title": n.get("新闻标题", n.get("title", "")),
                "content": (n.get("新闻内容", n.get("content", "")) or "")[:300],
                "date": n.get("发布时间", n.get("date", "")),
                "source": n.get("文章来源", n.get("source", "")),
                "link": n.get("新闻链接", n.get("link", "")),
                "interpretation": quick_interpret(n),
            }
            items.append(item)

        cache = {
            "code": code,
            "updated": "2026-06-13",
            "count": len(items),
            "items": items,
        }
        filepath = os.path.join(NEWS_DIR, f"{code}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    return len(codes_and_news)

def quick_interpret(news):
    title = news.get("新闻标题", news.get("title", ""))
    content = news.get("新闻内容", news.get("content", "")) or ""
    t = title + content[:100]

    rules = [
        ("H股" in t and "上市" in t, "筹划港股上市→拓宽融资渠道，利好长期"),
        ("减持" in t, "高管/股东减持→短期情绪偏空"),
        ("一季报" in t and ("增长" in t or "上涨" in t), "一季报业绩增长→基本面向好"),
        ("一季报" in t, "一季报已披露→关注营收和利润趋势"),
        ("涨停" in t or "大涨" in t, "短期受资金追捧→关注基本面支撑"),
        ("跳水" in t or "大跌" in t, "短期回调→关注成交量和后续走势"),
        ("中标" in t or "订单" in t or "合同" in t, "新订单/合同落地→利好营收增长"),
        ("成立" in t and "公司" in t, "新设子公司→布局新业务方向"),
        ("资金流出" in t, "主力资金出逃→注意短期回调风险"),
        ("资金流入" in t, "主力资金流入→短期偏多"),
        ("市值突破" in t, "市值突破重要关口→市场认可度提升"),
        ("年报" in t, "年报已出→关注业绩趋势和分红"),
        ("董事长" in t or "换届" in t, "管理层变动→关注新团队战略方向"),
        ("1260H" in t or "国防部" in t, "被列入外部清单→公司否认影响，需持续关注"),
        ("融资" in t and ("买入" in t or "净买入" in t), "融资客加仓→杠杆资金看多"),
    ]

    for condition, interpretation in rules:
        if condition:
            return interpretation

    # Default
    if "资金" in t: return "资金面动态→结合整体市场判断"
    if "涨" in t or "跌" in t: return "市场波动信息→关注后续走势"
    return ""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Read from arg
        data = json.loads(sys.argv[1])
        save_batch(data)
    print(f"Cached files: {len(os.listdir(NEWS_DIR))}")
