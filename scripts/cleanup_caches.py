#!/usr/bin/env python3
"""清理已有缓存：重跑 v2 过滤器（3天+去噪），删除无效缓存"""
import json, os, shutil

NEWS_DIR = r"C:\soft\agent\ai-dashboard\data\news"
from cache_news_v2 import process_batch, CUTOFF

def cleanup():
    files = [f for f in os.listdir(NEWS_DIR) if f.endswith('.json')]
    for f in sorted(files):
        path = os.path.join(NEWS_DIR, f)
        try:
            with open(path, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
        except:
            os.remove(path)
            continue

        code = data.get('code', '')
        items = data.get('items', [])

        # Re-filter: remove noise + old items
        keep = []
        for item in items:
            title = item.get('title', '')
            date = item.get('date', '')

            # Skip noise
            skip_kw = ["资金流出", "资金流入", "特大单", "融资客", "主力资金",
                       "大宗交易", "融资余额", "杠杆资金", "融资融券", "解密主力",
                       "融资净买入", "科创板主力", "获融资客", "获杠杆",
                       "融资融券余额", "股特大单净流入"]
            if any(kw in title for kw in skip_kw):
                continue

            # Skip old (>3 days)
            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(days=3)
            dt = None
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M"]:
                try:
                    dt = datetime.strptime(date[:19] if len(date)>=19 else date[:10], fmt)
                    break
                except:
                    continue
            if dt and dt < cutoff:
                continue

            keep.append(item)

        if keep:
            data['items'] = keep
            data['count'] = len(keep)
            with open(path, 'w', encoding='utf-8') as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
            print(f"  {code}: {len(keep)}/{len(items)} kept")
        else:
            os.remove(path)
            print(f"  {code}: removed (0/{len(items)} valid)")

    remaining = len([f for f in os.listdir(NEWS_DIR) if f.endswith('.json')])
    print(f"\nRemaining caches: {remaining}")

if __name__ == '__main__':
    cleanup()
