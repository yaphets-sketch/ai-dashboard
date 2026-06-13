#!/usr/bin/env python3
"""
AI 看板 v2 行情刷新 - 基于 akshare 多源 fallback
直接拉全 A 股实时行情，匹配 AI 股票池，输出 JSON
用法: python refresh_v2.py
"""
import json, os, sys
from datetime import datetime, timezone, timedelta

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"
QUOTES_FILE = r"C:\soft\agent\ai-dashboard\data\quotes.json"

# 东方财富常用字段 → 统一输出字段
FIELD_MAP_EM = {
    '代码': 'code', '名称': 'name',
    '最新价': 'price', '涨跌幅': 'change_pct',
    '总市值': 'market_cap', '市盈率-动态': 'pe',
    '市净率': 'pb', '成交量': 'volume', '成交额': 'amount',
    '换手率': 'turnover', '60日涨跌幅': 'change_60d',
}
FIELD_MAP_SINA = {
    '代码': 'code', '名称': 'name',
    '最新价': 'price', '涨跌幅': 'change_pct',
    # 新浪数据字段可能略有不同
}

def fetch_all_stocks():
    """多源 fallback 拉取全 A 股行情"""
    import akshare as ak

    # 1) 先试东方财富（字段最全）
    try:
        print("Trying Eastmoney...")
        df = ak.stock_zh_a_spot_em()
        if len(df) > 1000:
            print(f"  Eastmoney OK: {len(df)} stocks")
            # 统一列名
            df = df.rename(columns={k:v for k,v in FIELD_MAP_EM.items() if k in df.columns})
            return df
    except Exception as e:
        print(f"  Eastmoney failed: {type(e).__name__}")

    # 2) 降级到新浪
    try:
        print("Trying Sina...")
        df = ak.stock_zh_a_spot()
        if len(df) > 1000:
            print(f"  Sina OK: {len(df)} stocks")
            return df
    except Exception as e:
        print(f"  Sina failed: {type(e).__name__}")

    # 3) 降级到腾讯
    try:
        print("Trying Tencent...")
        df = ak.stock_zh_a_spot_tx()
        if len(df) > 1000:
            print(f"  Tencent OK: {len(df)} stocks")
            return df
    except Exception as e:
        print(f"  Tencent failed: {type(e).__name__}")

    raise RuntimeError("All data sources failed")

def main():
    # 1) 拉取全 A 股行情
    df = fetch_all_stocks()
    print(f"Fetched {len(df)} A-share stocks")

    # 2) 识别代码列
    code_col = None
    for col in ['代码', 'code']:
        if col in df.columns:
            code_col = col
            break
    if not code_col:
        print(f"Available columns: {list(df.columns)[:20]}")
        raise KeyError("Cannot find stock code column")

    # 3) 构建 name 和 price 映射（标准化代码格式）
    name_col = next((c for c in ['名称', 'name'] if c in df.columns), None)
    price_col = next((c for c in ['最新价', 'price', 'close'] if c in df.columns), None)
    change_col = next((c for c in ['涨跌幅', 'change_pct', 'pct_chg'] if c in df.columns), None)
    pe_col = next((c for c in ['市盈率-动态', 'pe', 'PE'] if c in df.columns), None)
    mcap_col = next((c for c in ['总市值', 'market_cap'] if c in df.columns), None)
    pb_col = next((c for c in ['市净率', 'pb', 'PB'] if c in df.columns), None)

    # Build lookup by clean code
    lookup = {}
    for _, row in df.iterrows():
        raw = str(row[code_col]).strip()
        # Handle market prefixes like sh600519, sz000001
        for prefix in ['sh', 'sz', 'bj']:
            if raw.lower().startswith(prefix):
                raw = raw[len(prefix):]
                break
        # Remove any remaining non-digit chars
        code = ''.join(c for c in raw if c.isdigit())[:6]
        if len(code) == 6:
            lookup[code] = {
                'name': str(row[name_col]) if name_col and name_col in df.columns else '',
                'price': safe_float(row.get(price_col)) if price_col else 0,
                'change_pct': safe_float(row.get(change_col)) if change_col else 0,
                'pe': safe_float(row.get(pe_col)) if pe_col else 0,
                'market_cap': safe_float(row.get(mcap_col)) if mcap_col else 0,
                'pb': safe_float(row.get(pb_col)) if pb_col else 0,
            }
    print(f"Lookup: {len(lookup)} unique codes")

    # 4) 加载 universe
    with open(UNIVERSE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 5) 更新行情
    updated = 0
    named = 0
    for stock in data['stocks']:
        code = stock['code']
        if code in lookup:
            info = lookup[code]
            stock['price'] = info['price'] or stock.get('price', 0)
            stock['change_pct'] = info['change_pct'] or stock.get('change_pct', 0)
            stock['pe'] = info['pe'] or stock.get('pe', 0)
            stock['market_cap'] = info['market_cap'] or stock.get('market_cap', 0)
            stock['pb'] = info['pb'] or stock.get('pb', 0)
            # Fill name if we don't have one
            if not stock.get('name') or stock['name'] == code:
                stock['name'] = info['name']
                named += 1
            updated += 1

    tz = timezone(timedelta(hours=8))
    now_str = datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S+08:00')
    data['updated'] = now_str

    with open(UNIVERSE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Updated {updated}/{data['total']} stocks (+{named} names)")

    # 6) 写 quotes.json
    quotes_data = {
        "updated": now_str,
        "source": "akshare-sina" if '新浪' in str(type(df)) else "akshare-eastmoney",
        "stocks": [
            {
                "code": s['code'], "name": s['name'],
                "price": s['price'], "change_pct": s['change_pct'],
                "market_cap": s['market_cap'], "pe": s['pe'], "pb": s['pb'],
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
        if val is None: return 0
        if isinstance(val, str): val = val.replace('%','').replace(',','')
        return float(val)
    except (ValueError, TypeError):
        return 0

if __name__ == '__main__':
    main()
