#!/usr/bin/env python3
"""生成自包含HTML：数据内嵌，双击即用，离线可看"""
import json, os

UNIVERSE = r"C:\soft\agent\ai-dashboard\data\universe.json"
OUTPUT = r"C:\soft\agent\ai-dashboard\ai-dashboard.html"

# 精简数据（只保留前端需要的字段）
def slim_stock(s):
    return {
        "code": s["code"], "name": s["name"],
        "price": s.get("price",0), "change_pct": s.get("change_pct",0),
        "market_cap": s.get("market_cap",0), "pe": s.get("pe",0), "pb": s.get("pb",0),
        "category": s.get("category","other"),
        "core_business": s.get("core_business",""),
        "concepts": s.get("concepts",[])[:4],
        "q1_revenue": s.get("q1_revenue"), "q1_profit": s.get("q1_profit"),
        "q1_gross_margin": s.get("q1_gross_margin"),
        "q1_revenue_yoy": s.get("q1_revenue_yoy"),
        "deep_analysis": {
            "products": s.get("deep_analysis",{}).get("products",[]),
            "supply_chain": s.get("deep_analysis",{}).get("supply_chain",{}),
            "catalysts": s.get("deep_analysis",{}).get("catalysts",[]),
            "risks": s.get("deep_analysis",{}).get("risks",[]),
            "key_question": s.get("deep_analysis",{}).get("key_question",""),
        }
    }

def main():
    with open(UNIVERSE, "r", encoding="utf-8") as f:
        data = json.load(f)

    stocks = [slim_stock(s) for s in data["stocks"]]
    stocks_json = json.dumps({"updated": data.get("updated",""), "stocks": stocks}, ensure_ascii=False)

    # Read the web HTML
    with open(r"C:\soft\agent\ai-dashboard\web\index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Add inline data support - insert check at start of loadData
    old = "async function loadData(){\n  try{\n    const r=await fetch('/data/universe.json?t='+Date.now());"
    new = "async function loadData(){\n  if(typeof __INLINE_DATA__!=='undefined'){allStocks=__INLINE_DATA__.stocks||[];document.getElementById('updateTime').textContent='离线版: '+(__INLINE_DATA__.updated||'');updateStats();renderStockList();return;}\n  try{\n    const r=await fetch('/data/universe.json?t='+Date.now());"
    html = html.replace(old, new)

    # Replace news fetch with empty response
    old_news = "await fetch(`/data/news/${code}.json?t=${Date.now()}`)"
    new_news = "Promise.reject('offline')"
    html = html.replace(old_news, new_news)

    # Replace stat fetch
    old_stat = "fetch('/data/news/_count')"
    new_stat = "Promise.resolve({text:()=>Promise.resolve('"+str(len([f for f in os.listdir(r'C:\soft\agent\ai-dashboard\data\news') if f.endswith('.json')]))+"')})"
    html = html.replace(old_stat, new_stat)

    # Inject data before init
    inject = f"<script>const __INLINE_DATA__ = {stocks_json};</script>"
    html = html.replace("</head>", inject + "\n</head>")

    # Add PWA manifest + apple-touch-icon for mobile install
    pwa_inject = f'''<link rel="manifest" href="data:application/json,{{"name":"AI科技股看板","short_name":"AI看板","start_url":".","display":"standalone","background_color":"#080b12","theme_color":"#3b82f6","icons":[{{"src":"data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📊</text></svg>","sizes":"100x100","type":"image/svg+xml"}}]}}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="AI看板">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'''
    html = html.replace('</head>', pwa_inject + '\n</head>', 1)

    # Update footer
    html = html.replace("数据来源: 腾讯行情 + 同花顺财报 + 公开新闻 | 每日19:00自动更新 | 不构成投资建议",
                         f"离线版 | 数据: {data.get('updated','')} | 可安装到手机桌面 | 每日自动更新")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = os.path.getsize(OUTPUT) / (1024*1024)
    print(f"Generated: {OUTPUT}")
    print(f"Size: {size_mb:.1f} MB")
    print(f"Stocks: {len(stocks)}")
    print(f"Double-click to open. Works offline.")

if __name__ == "__main__":
    main()
