#!/usr/bin/env python3
"""全A股AI标的扩展：按行业+概念关键词筛选"""
import json, os, sys

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"

# AI相关行业关键词（匹配同花顺/东方财富行业分类）
AI_INDUSTRIES = [
    "半导体", "芯片", "集成电路", "电子", "光电子", "光学",
    "通信设备", "通信服务", "通信网络",
    "软件开发", "软件", "IT服务", "信息技术", "计算机",
    "互联网", "云计算", "大数据", "人工智能",
    "自动化", "机器人", "智能",
    "消费电子", "电子元件", "PCB", "元器件",
    "军工电子", "航天", "卫星",
    "电子化学品", "新材料",
]

# AI相关概念关键词
AI_CONCEPTS = [
    "人工智能", "AI", "芯片", "半导体", "算力", "CPO", "光通信", "光模块",
    "机器人", "机器视觉", "传感器", "物联网", "5G", "6G", "F5G",
    "云计算", "大数据", "数据中心", "液冷", "服务器",
    "信创", "国产替代", "操作系统", "数据安全", "数据要素",
    "自动驾驶", "无人驾驶", "激光雷达", "智能座舱", "车联网",
    "数字经济", "数字孪生", "元宇宙", "区块链",
    "鸿蒙", "华为", "英伟达", "DeepSeek", "ChatGPT",
    "量子", "脑机", "人形", "语音", "人脸识别",
    "消费电子", "智能穿戴", "AI PC", "AI手机", "AI眼镜",
    "PCB", "封装", "存储", "MCU", "FPGA", "EDA",
    "光刻", "碳化硅", "氮化镓", "第三代半导体",
    "低空经济", "eVTOL", "飞行汽车",
]

def classify_by_name(name, biz):
    """根据名字和业务分配分类"""
    t = (name + (biz or "")).lower()
    if any(k in t for k in ["光模块","光器件","光芯片","光通信","光纤","光缆","cpo"]): return "optical"
    if any(k in t for k in ["芯片","半导体","封测","晶圆","存储","mcu","fpga","eda","集成电路","ic"]): return "chip"
    if any(k in t for k in ["算力","服务器","数据中心","idc","液冷","云服务","云计算","云"]): return "compute"
    if any(k in t for k in ["机器人","减速器","伺服","自动化","机器视觉"]): return "robot"
    if any(k in t for k in ["人工智能","ai应用","ai平台","大模型","智能","软件","saas"]): return "app"
    if any(k in t for k in ["安全","信创","操作系统","数据要素","数据管理"]): return "app"
    if any(k in t for k in ["通信","5g","6g","基站","天线","射频","连接器","交换机"]): return "infra"
    if any(k in t for k in ["pcb","元器件","被动元件","覆铜板","载板","电子材料","传感器"]): return "chip"
    return "other"

def main():
    # Load existing universe
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    existing = {s["code"] for s in data["stocks"]}

    # Fetch all A-share stocks from akshare (Sina source)
    print("Fetching all A-share stocks...")
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot()
        print(f"  Got {len(df)} stocks")
    except Exception as e:
        print(f"  akshare failed: {e}, trying Tencent...")
        # Try to load from Tencent
        df = None

    if df is None:
        print("Cannot fetch stock list. Aborting.")
        return

    # Identify code and name columns
    code_col = next((c for c in df.columns if c in ['代码', 'code']), None)
    name_col = next((c for c in df.columns if c in ['名称', 'name']), None)
    if not code_col:
        print(f"Columns: {list(df.columns)[:15]}")
        return

    # Filter for AI-related stocks
    new_stocks = []
    for _, row in df.iterrows():
        raw_code = str(row[code_col]).strip()
        # Strip market prefix
        for prefix in ['sh', 'sz', 'bj']:
            if raw_code.lower().startswith(prefix):
                raw_code = raw_code[len(prefix):]
                break
        code = ''.join(c for c in raw_code if c.isdigit())[:6]
        if len(code) != 6 or code in existing:
            continue

        name = str(row[name_col]) if name_col and name_col in df.columns else ""

        # Check if name/business matches AI keywords
        name_lower = name.lower()
        is_ai = False
        for kw in AI_CONCEPTS:
            if kw.lower() in name_lower:
                is_ai = True
                break

        if not is_ai:
            continue

        cat = classify_by_name(name, "")
        new_stocks.append({
            "code": code,
            "name": name,
            "market": "sh" if code.startswith("6") else "sz",
            "core_business": "",
            "category": cat,
            "price": 0, "change_pct": 0, "market_cap": 0, "pe": 0, "pb": 0,
            "concepts": [], "latest_news": [],
            "revenue_detail": "", "added_price": 0, "added_date": "20260613",
        })

    # Deduplicate by code
    seen = set()
    unique = []
    for s in new_stocks:
        if s["code"] not in seen:
            seen.add(s["code"])
            unique.append(s)

    print(f"New AI stocks found: {len(unique)}")
    data["stocks"].extend(unique)
    data["total"] = len(data["stocks"])

    # Update categories
    from collections import Counter
    cats = Counter(s["category"] for s in data["stocks"])
    print(f"Categories: {dict(cats)}")

    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Total: {data['total']} stocks")

if __name__ == "__main__":
    main()
