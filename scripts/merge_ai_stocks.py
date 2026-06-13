#!/usr/bin/env python3
"""从多个来源提取所有AI相关A股代码，合并去重写入universe.json"""
import json, os, re

DATA_DIR = r"C:\soft\agent\ai-dashboard\data"
UNIVERSE_FILE = os.path.join(DATA_DIR, "universe.json")

# 来源1: kissdown.cn 人工智能+云计算 123只
KISSDOWN_STOCKS = """
600770,600322,601138,600449,600355,600476,600718,603660,600570,600756,
601360,603528,600654,600797,600633,600728,603636,603019,600850,603171,
600602,600410,301396,301248,300297,300687,301428,300608,300033,301172,
300249,300872,300002,300030,300365,300578,300047,300078,301390,300212,
300287,300085,300603,300213,301503,300768,300065,300020,300645,301185,
300235,300730,301380,300188,300231,300448,300168,300925,300674,300469,
301316,300380,300166,300113,300229,300454,300663,300369,300366,300339,
300017,300378,300634,301159,300044,300271,301171,300379,300036,300419,
000066,000034,002984,002415,002439,002316,002352,002474,002236,002929,
002197,002195,002955,002339,002229,002642,000938,002410,002063,002908,
002279,002467,002065,002298,002315,000977,000063,002657,002268,002093,
002649,002396,001389,002123,002362,000070,002301,002771,000158,002253,
000555,002261,002912
"""

# 来源2: DOIT 算力产业
DOIT_STOCKS = """
688041,688256,688001,601138,000977,603019,000938,603118,300308,300682,
300223,688525,603986,600941,601728,688227,000063,000034,300454,600410,
300166,002212,002197,600588,300846,300383,688316,688158,600845,603881,
600804,300017,002229,600186,002261,603496,002849
"""

# 来源3: 淘股吧 AI四层产业链 (手动补关键标的)
TGU_STOCKS = """
688041,688256,688047,688001,603019,000977,000938,300308,300502,300394,
002281,300620,688498,688313,688205,688195,002463,002916,688525,603986,
688008,688981,002371,600584,688012,688120,688170,601138,002384,688017,
002156,300913,688048,601869,600487,600522,688629,688766,600183,002938,
603678,688220,300548,300570,688143,301191
"""

# 来源4: 额外AI应用/软件/概念标的
EXTRA_AI = """
002230,002362,300229,300624,300033,688111,688088,300454,300369,002439,
002415,002236,300188,603881,300383,300017,600845,688158,688316,300846,
301236,688561,688475,688521,688313,003021,002049,688072,300661,603290,
688262,688416,688521,688206,688187,688475,300661,301269,688305,688160,
688333,688366,688155
"""

def parse_codes(text):
    """从文本中提取6位数字代码"""
    return re.findall(r'\b(\d{6})\b', text.replace(',', ' '))

def main():
    # Parse all sources
    all_codes = set()
    all_codes.update(parse_codes(KISSDOWN_STOCKS))
    all_codes.update(parse_codes(DOIT_STOCKS))
    all_codes.update(parse_codes(TGU_STOCKS))
    all_codes.update(parse_codes(EXTRA_AI))

    # Load existing universe
    with open(UNIVERSE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_codes = {s['code'] for s in data['stocks']}
    existing_stocks = {s['code']: s for s in data['stocks']}

    new_codes = all_codes - existing_codes
    print(f"Existing: {len(existing_codes)}")
    print(f"New from AI sources: {len(new_codes)}")

    # For new stocks, create basic entries
    new_stocks = []
    for code in sorted(new_codes):
        market = "sh" if code.startswith('6') else "sz"
        new_stocks.append({
            "code": code,
            "name": code,  # placeholder, will be updated
            "market": market,
            "core_business": "",
            "category": "other",
            "price": 0,
            "change_pct": 0,
            "market_cap": 0,
            "pe": 0,
            "pb": 0,
            "concepts": [],
            "latest_news": [],
            "revenue_detail": "",
            "added_price": 0,
            "added_date": "20260613",
        })

    data['stocks'].extend(new_stocks)
    data['total'] = len(data['stocks'])
    data['updated'] = "2026-06-13T17:00:00+08:00"

    with open(UNIVERSE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Total after merge: {data['total']}")
    print(f"\nNew codes ({len(new_codes)}):")
    for s in new_stocks[:30]:
        print(f"  {s['code']}")

if __name__ == '__main__':
    main()
