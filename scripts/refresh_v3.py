#!/usr/bin/env python3
"""
v3 行情刷新 - 直连腾讯财经 API
支持批量拉取（单次最多50只），含价格/涨跌幅/PE/市值
比 akshare 更快更稳定
"""
import json, os, urllib.request, re
from datetime import datetime, timezone, timedelta

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"
QUOTES_FILE = r"C:\soft\agent\ai-dashboard\data\quotes.json"
TENCENT_API = "http://qt.gtimg.cn/q="

def fetch_batch(codes):
    """腾讯批量行情：最多50只，返回 {code: {price, change_pct, pe, market_cap, pb, volume}}"""
    market_codes = []
    for c in codes:
        prefix = "sh" if c.startswith(("6","9")) else "sz"
        market_codes.append(f"{prefix}{c}")

    url = TENCENT_API + ",".join(market_codes)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=15)
        data = r.read().decode("gbk", errors="replace")
    except Exception as e:
        print(f"  Fetch error: {e}")
        return {}

    result = {}
    for line in data.strip().split("\n"):
        if "~" not in line:
            continue
        # 提取引号内容
        m = re.search(r'"([^"]+)"', line)
        if not m:
            continue
        parts = m.group(1).split("~")
        if len(parts) < 50:
            continue

        # 腾讯字段索引（部分关键）：
        # [1]=名称 [2]=代码 [3]=最新价 [4]=昨收 [5]=今开
        # [6]=成交量(手) [9]=最高 [10]=最低
        # [31]=涨跌幅% [39]=PE(动态) [43]=市净率PB
        # [45]=总市值(亿) [44]=流通市值(亿)
        try:
            code = parts[2].strip()
            name = parts[1].strip()
            price = safe_float(parts[3])
            last_close = safe_float(parts[4])
            change_pct = safe_float(parts[32]) if len(parts) > 32 else 0
            if change_pct == 0 and last_close > 0:
                change_pct = round((price - last_close) / last_close * 100, 2)
            pe = safe_float(parts[39]) if len(parts) > 39 else 0
            pb = safe_float(parts[43]) if len(parts) > 43 else 0
            market_cap = safe_float(parts[45]) if len(parts) > 45 else 0  # 亿元

            result[code] = {
                "name": name,
                "price": price,
                "change_pct": change_pct,
                "pe": pe,
                "pb": pb,
                "market_cap": market_cap * 1e8 if market_cap > 0 else 0,  # 转为元
            }
        except (IndexError, ValueError):
            continue

    return result

def safe_float(s):
    try: return float(s) if s and s.strip() else 0
    except: return 0

def main():
    # 加载股票池
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    codes = [s["code"] for s in data["stocks"]]

    # 分批拉取（50只/批）
    all_quotes = {}
    batch_size = 50
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        quotes = fetch_batch(batch)
        all_quotes.update(quotes)
        print(f"  Batch {i//batch_size+1}: {len(batch)} requested, {len(quotes)} received")

    # 更新 universe.json
    updated = 0
    for stock in data["stocks"]:
        code = stock["code"]
        if code in all_quotes:
            q = all_quotes[code]
            stock["price"] = q["price"]
            stock["change_pct"] = q["change_pct"]
            stock["pe"] = q["pe"]
            stock["pb"] = q["pb"]
            stock["market_cap"] = q["market_cap"]
            if not stock.get("name") or stock["name"] == code:
                stock["name"] = q["name"]
            updated += 1

    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S+08:00")
    data["updated"] = now
    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 写 quotes.json
    quotes_data = {
        "updated": now,
        "source": "tencent-qt",
        "stocks": [{
            "code": s["code"], "name": s["name"],
            "price": s["price"], "change_pct": s["change_pct"],
            "market_cap": s["market_cap"], "pe": s["pe"], "pb": s["pb"],
            "category": s["category"],
            "core_business": s.get("core_business", ""),
            "concepts": s.get("concepts", []),
        } for s in data["stocks"]]
    }
    with open(QUOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(quotes_data, f, ensure_ascii=False, indent=2)

    # Stats
    with_price = sum(1 for s in data["stocks"] if s["price"] > 0)
    with_pe = sum(1 for s in data["stocks"] if s["pe"] > 0)
    print(f"\nUpdated: {updated}/{data['total']}")
    print(f"With price: {with_price}, With PE: {with_pe}")
    print(f"Source: Tencent qt.gtimg.cn")
    print(f"Written: {UNIVERSE_FILE} & {QUOTES_FILE}")

if __name__ == "__main__":
    main()
