#!/usr/bin/env python3
"""
处理 get_stock_list 的 MCP 返回数据，更新 universe.json 的行情字段。
用法: python refresh_quotes.py <mcp_result_file.json>
"""
import json, sys, os

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"
QUOTES_FILE = r"C:\soft\agent\ai-dashboard\data\quotes.json"

def load_mcp_result(filepath):
    """加载 MCP get_stock_list 返回的原始 JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    # Handle different MCP response formats
    if isinstance(raw, dict):
        result = raw.get('result', raw.get('data', raw))
        if isinstance(result, str):
            result = json.loads(result)
        return result
    return raw

def main():
    if len(sys.argv) < 2:
        # No file provided - create empty quotes
        update_universe_from_scratch()
        return

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    stock_list = load_mcp_result(filepath)

    # Build lookup: code -> {name, price, change_pct, pe, market_cap}
    lookup = {}
    for s in stock_list:
        raw_code = s.get('代码', s.get('code', ''))
        # Strip market prefix
        code = raw_code[2:] if len(raw_code) >= 8 and raw_code[:2] in ('sh','sz','bj') else raw_code
        if not code or len(code) != 6:
            continue

        lookup[code] = {
            'name': s.get('名称', s.get('name', '')),
            'price': safe_float(s.get('最新价', s.get('price', 0))),
            'change_pct': safe_float(s.get('涨跌幅', s.get('change_pct', 0))),
            'pe': safe_float(s.get('市盈率', s.get('PE', 0))),
            'market_cap': safe_float(s.get('总市值', s.get('market_cap', 0))),
        }

    print(f"Loaded {len(lookup)} stocks from MCP data")

    # Update universe.json
    with open(UNIVERSE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    for stock in data['stocks']:
        code = stock['code']
        if code in lookup:
            info = lookup[code]
            stock['price'] = info['price'] or stock.get('price', 0)
            stock['change_pct'] = info['change_pct'] or stock.get('change_pct', 0)
            stock['pe'] = info['pe'] or stock.get('pe', 0)
            stock['market_cap'] = info['market_cap'] or stock.get('market_cap', 0)
            if not stock.get('name') or stock['name'] == code:
                stock['name'] = info['name']
            updated += 1

    from datetime import datetime, timezone, timedelta
    tz = timezone(timedelta(hours=8))
    data['updated'] = datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S+08:00')

    with open(UNIVERSE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Updated {updated}/{data['total']} stocks")
    print(f"Timestamp: {data['updated']}")

    # Also write quotes.json for frontend
    quotes_data = {
        "updated": data['updated'],
        "stocks": [
            {
                "code": s['code'],
                "name": s['name'],
                "price": s['price'],
                "change_pct": s['change_pct'],
                "market_cap": s['market_cap'],
                "pe": s['pe'],
                "category": s['category'],
                "core_business": s.get('core_business', ''),
                "concepts": s.get('concepts', []),
            }
            for s in data['stocks']
        ]
    }
    with open(QUOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(quotes_data, f, ensure_ascii=False, indent=2)
    print(f"Written quotes.json ({len(quotes_data['stocks'])} stocks)")

def safe_float(val):
    try:
        return float(val) if val else 0
    except (ValueError, TypeError):
        return 0

def update_universe_from_scratch():
    """Without MCP data, just update timestamps"""
    with open(UNIVERSE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    from datetime import datetime, timezone, timedelta
    tz = timezone(timedelta(hours=8))
    data['updated'] = datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S+08:00')
    with open(UNIVERSE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Timestamp refreshed: {data['updated']}")

if __name__ == '__main__':
    main()
