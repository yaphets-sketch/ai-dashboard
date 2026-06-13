#!/usr/bin/env python3
"""批量拉取Q1 2026财报数据"""
import json, os, sys, time
from datetime import datetime
import akshare as ak

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"
BATCH_SIZE = 10
DELAY = 0.5  # seconds between batches

def fetch_one(code):
    try:
        df = ak.stock_financial_abstract_ths(symbol=code, indicator='按报告期')
        if df is None or len(df) == 0:
            return None
        # Find Q1 2026 row
        q1 = df[df['报告期'].astype(str).str.contains('2026-03-31')]
        if len(q1) == 0:
            q1 = df[df['报告期'].astype(str).str.contains('2026')]
        if len(q1) == 0:
            return None
        row = q1.iloc[-1]  # Latest 2026 quarter
        return {
            'revenue': safe_float(row.get('营业总收入', 0)),
            'profit': safe_float(row.get('净利润', 0)),
            'profit_yoy': safe_float(row.get('净利润同比增长率', 0)),
            'revenue_yoy': safe_float(row.get('营业总收入同比增长率', 0)),
            'eps': safe_float(row.get('基本每股收益', 0)),
            'roe': safe_float(row.get('净资产收益率', 0)),
            'gross_margin': safe_float(row.get('销售毛利率', 0)),
        }
    except Exception as e:
        return None

def safe_float(val):
    """智能单位转换：亿→直接，万→/10000"""
    try:
        if val is None: return 0
        if isinstance(val, (int, float)): return float(val)
        s = str(val).replace('%','').replace(',','').strip()
        # 检测单位
        if '亿' in s:
            return float(s.replace('亿',''))
        elif '万' in s:
            return float(s.replace('万','')) / 10000
        else:
            # 纯数字，假定为元→转亿
            f = float(s) if s else 0
            return f / 1e8 if abs(f) > 1e6 else f  # >100万则假定为元
    except:
        return 0

def main():
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    codes = [s["code"] for s in data["stocks"]]
    total = len(codes)
    fetched = 0
    updated = 0

    for i in range(0, total, BATCH_SIZE):
        batch = codes[i:i+BATCH_SIZE]
        for code in batch:
            result = fetch_one(code)
            fetched += 1
            if result:
                for s in data["stocks"]:
                    if s["code"] == code:
                        s["q1_revenue"] = result["revenue"]
                        s["q1_profit"] = result["profit"]
                        s["q1_profit_yoy"] = result["profit_yoy"]
                        s["q1_revenue_yoy"] = result["revenue_yoy"]
                        s["q1_eps"] = result["eps"]
                        s["q1_roe"] = result["roe"]
                        s["q1_gross_margin"] = result["gross_margin"]
                        updated += 1
                        break
            if fetched % 20 == 0:
                print(f"  {fetched}/{total} ({updated} with data)...", end='\r')
        time.sleep(DELAY)

    print(f"\nFetched: {fetched}/{total}, With Q1 data: {updated}")

    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Updated: {UNIVERSE_FILE}")

if __name__ == "__main__":
    main()
