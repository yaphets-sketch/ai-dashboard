#!/usr/bin/env python3
"""
重建全部新闻缓存：单源 HiSZ get_stock_news + 3天过滤 + 去噪
用法: 将 MCP 批量返回的 JSON 通过 stdin 或参数传入
"""
import json, os, sys
from datetime import datetime, timedelta

NEWS_DIR = r"C:\soft\agent\ai-dashboard\data\news"
os.makedirs(NEWS_DIR, exist_ok=True)
CUTOFF_NORMAL = datetime.now() - timedelta(days=7)   # 普通新闻7天
CUTOFF_IMPORTANT = datetime.now() - timedelta(days=45) # 季报/重大事件45天

def importance(title, content):
    """判断新闻重要性：high > normal"""
    t = title + (content or "")[:100]
    high_kw = ["一季报", "年报", "业绩", "净利润", "营收", "收购", "重组",
               "中标", "订单", "合同", "增持", "回购", "分红", "H股",
               "上市", "发行", "募资", "定增", "股东会", "换届",
               "历史新高", "涨停", "市值突破"]
    for kw in high_kw:
        if kw in t:
            return "high"
    return "normal"

# 纯噪音标题关键词（不含实质性公司信息的市场统计）
NOISE_KW = [
    "资金流出榜", "资金流入榜", "资金流向日报", "资金流向排名",
    "特大单净流入", "特大单净流出", "股特大单净流入",
    "主力资金净流入排名", "主力资金净流出排名",
    "主力资金净流入", "主力资金净流出", "主力动向",
    "融资客净买入金额排名", "融资客看好", "融资客大手笔",
    "融资净买入居前", "获融资客大手", "获杠杆资金",
    "融资融券余额每日变动", "融资余额增加", "杠杆资金大手笔",
    "杠杆资金净买入", "融资余额超",
    "大宗交易成交明细", "科创板股今日大宗", "今日大宗交易",
    "解密主力资金出逃", "解密主力",
    "科创板主力资金净流出", "科创板主力资金净流入",
    "股获杠杆资金净买入", "股特大单净流入资金",
    "只科创板股融资余额增加", "只股获融资客",
    "行业资金流出榜", "行业今日净流出", "行业今日涨",
    "股受融资客青睐", "融资客净买入",
]

def parse_date(s):
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
        try: return datetime.strptime(s[:19] if len(s)>=19 else s[:10], fmt)
        except: continue
    return None

def is_noise(title):
    for kw in NOISE_KW:
        if kw in title:
            return True
    return False

def quick_interpret(title, content):
    t = title + (content or "")[:100]
    if "H股" in t and "上市" in t: return "筹划港股上市→拓宽融资渠道，利好长期"
    if "减持" in t: return "股东减持→短期情绪偏空，关注量级"
    if "一季报" in t and ("增长" in t or "上涨" in t): return "业绩增长→基本面向好"
    if "一季报" in t or "年报" in t: return "财报已出→关注营收利润趋势"
    if "涨停" in t or "大涨" in t: return "资金追捧→关注是否有基本面支撑"
    if "跳水" in t or "大跌" in t: return "短期回调→关注成交量和后续走势"
    if "中标" in t or "订单" in t or "合同" in t: return "新单/合同落地→利好营收增长"
    if "成立" in t and "公司" in t: return "新设公司→布局新业务方向"
    if "发布" in t and ("产品" in t or "平台" in t): return "新品/平台发布→关注市场反馈"
    if "上市" in t and "H" in t: return "赴港上市→国际化战略布局"
    if "董事长" in t or "换届" in t or "总裁" in t: return "管理层变动→关注新团队战略方向"
    if "1260H" in t or "国防部" in t: return "被列入外部清单→公司否认，持续关注后续"
    if "收购" in t: return "并购动作→关注标的和整合进展"
    if "回购" in t: return "股份回购→利好股价，体现公司信心"
    return ""

def save_one(code, raw_items):
    """处理单个股票的新闻列表并缓存"""
    items = []
    for n in raw_items:
        title = n.get("新闻标题", n.get("title", ""))
        if is_noise(title):
            continue
        dt = parse_date(n.get("发布时间", n.get("date", "")))
        if not dt:
            continue
        imp = importance(title, n.get("新闻内容", n.get("content", "")))
        cutoff = CUTOFF_IMPORTANT if imp == "high" else CUTOFF_NORMAL
        if dt < cutoff:
            continue

        items.append({
            "title": title,
            "content": (n.get("新闻内容", n.get("content", "")) or "")[:250],
            "date": n.get("发布时间", n.get("date", ""))[:16],
            "source": n.get("文章来源", n.get("source", "")),
            "interpretation": "",
        })

    # 标记解读
    for item in items:
        item["interpretation"] = quick_interpret(item["title"], item["content"])

    # 最多保留 6 条
    items = items[:6]

    cache = {"code": code, "updated": datetime.now().strftime("%Y-%m-%d %H:%M"), "count": len(items), "items": items}
    filepath = os.path.join(NEWS_DIR, f"{code}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    status = "+" if items else "-"
    print(f"  [{status}] {code}: {len(items)} items")
    return cache

if __name__ == "__main__":
    if len(sys.argv) > 1:
        data = json.loads(sys.argv[1])
        for code, raw in data:
            save_one(code, raw)
    print(f"\nTotal cached: {len(os.listdir(NEWS_DIR))}")
