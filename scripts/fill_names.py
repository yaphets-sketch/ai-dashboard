#!/usr/bin/env python3
"""从 get_stock_list 大文件中提取名字/价格/PE/市值，更新 universe.json"""
import json, os

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"
STOCKLIST_FILE = r"C:\Users\44627\AppData\Roaming\CherryStudio\.claude\projects\C--soft-agent\e7f50411-f3b8-450f-a3e9-0da60bb1f9be\tool-results\mcp-HiSZvpvXDmqyjt11UHF5j-get_stock_list-1781337228780.txt"

def main():
    # Load the stock list
    with open(STOCKLIST_FILE, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    stock_list = raw if isinstance(raw, list) else raw.get('result', raw.get('data', []))
    if isinstance(stock_list, str):
        stock_list = json.loads(stock_list)

    print(f"Loaded {len(stock_list)} stocks from market list")

    # Build lookup (strip market prefix from codes)
    lookup = {}
    for s in stock_list:
        raw_code = s.get('代码', s.get('code', ''))
        # Strip sh/sz/bj prefix
        code = raw_code[2:] if len(raw_code) >= 8 and raw_code[:2] in ('sh','sz','bj') else raw_code
        if code and len(code) == 6:
            lookup[code] = {
                'name': s.get('名称', s.get('name', '')),
                'price': float(s.get('最新价', s.get('price', 0)) or 0),
                'change_pct': float(s.get('涨跌幅', s.get('change_pct', 0)) or 0),
            }
    print(f"Lookup built: {len(lookup)} entries")

    # Load universe
    with open(UNIVERSE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    for stock in data['stocks']:
        code = stock['code']
        if code in lookup:
            info = lookup[code]
            if stock.get('name') == code or stock['name'] == '' or stock['name'] == stock['code']:
                stock['name'] = info['name']
                updated += 1
            if stock.get('price', 0) == 0 and info['price'] > 0:
                stock['price'] = info['price']
                stock['change_pct'] = info['change_pct']

    data['updated'] = "2026-06-13T17:30:00+08:00"

    with open(UNIVERSE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    unnamed = sum(1 for s in data['stocks'] if s['name'] == s['code'] or s['name'] == '')
    print(f"Updated: {updated} names")
    print(f"Still unnamed: {unnamed}")
    print(f"Total stocks: {data['total']}")

if __name__ == '__main__':
    main()
