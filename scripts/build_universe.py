#!/usr/bin/env python3
"""构建 AI 股票池初始数据"""
import json, os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

# AI 核心业务与分类映射（基于已知信息）
CORE_BUSINESS = {
    # 光模块
    "300308": ("高速光模块(800G/1.6T)", "optical"),
    "300502": ("高速光模块(800G)", "optical"),
    "300394": ("光器件/光模块上游", "optical"),
    "002281": ("光模块/光器件", "optical"),
    "300620": ("光器件/芯片", "optical"),
    "300548": ("光器件/PLC芯片", "optical"),
    "300570": ("光连接器/器件", "optical"),
    "688205": ("高速光芯片/电芯片", "optical"),
    "688498": ("光芯片(IDM)", "optical"),
    "688313": ("光芯片/PLC分路器", "optical"),
    "688195": ("光器件/透镜", "optical"),
    "300913": ("高速铜缆连接器", "optical"),
    "301191": ("光器件/陶瓷基板", "optical"),
    "601869": ("光纤预制棒/光缆", "optical"),
    "600487": ("光纤光缆/海洋通信", "optical"),
    "600522": ("光纤光缆/海洋通信", "optical"),
    "600345": ("光纤光缆", "optical"),
    # 光芯片
    "688048": ("激光器芯片(EML)", "optical"),
    # AI 芯片/GPU
    "688041": ("国产AI芯片(DCU)", "chip"),
    "688256": ("国产AI芯片(思元)", "chip"),
    "688047": ("国产CPU", "chip"),
    "603019": ("国产算力服务器", "chip"),
    "688008": ("内存接口芯片", "chip"),
    "688981": ("晶圆代工", "chip"),
    "002371": ("半导体设备", "chip"),
    # 封测
    "600584": ("半导体封测", "chip"),
    "002156": ("半导体封测", "chip"),
    # PCB
    "002463": ("AI服务器PCB", "chip"),
    "002916": ("IC载板/PCB", "chip"),
    "002938": ("HDI/类载板", "chip"),
    # 存储
    "688525": ("存储芯片/模组", "chip"),
    "688766": ("NOR Flash", "chip"),
    # 连接器/结构件
    "688629": ("高速连接器", "infra"),
    "601138": ("AI服务器/AI算力", "compute"),
    # 其他
    "600183": ("覆铜板/PCB材料", "chip"),
    "002384": ("PCB/精密制造", "chip"),
    "688981": ("晶圆代工", "chip"),
}

def main():
    # 读取自选股
    self_stocks_path = os.path.join(DATA_DIR, '..', '..', 'stock_data_output', 'ths_self_stocks.json')
    stocks = []

    if os.path.exists(self_stocks_path):
        with open(self_stocks_path, 'r', encoding='utf-8') as f:
            raw_stocks = json.load(f)

        for s in raw_stocks:
            code = s['code']
            biz_info = CORE_BUSINESS.get(code, (None, 'other'))
            stock = {
                "code": code,
                "name": s['name'],
                "market": "sh" if s.get('market') == '17' or code.startswith('6') else "sz",
                "core_business": biz_info[0] or "",
                "category": biz_info[1],
                "price": 0,
                "change_pct": 0,
                "market_cap": 0,
                "pe": 0,
                "pb": 0,
                "concepts": [],
                "latest_news": [],
                "revenue_detail": "",
                "added_price": s.get('added_price', 0),
                "added_date": s.get('added_date', ''),
            }
            stocks.append(stock)

    # 写 universe.json
    universe = {
        "updated": "2026-06-13T00:00:00+08:00",
        "total": len(stocks),
        "stocks": stocks
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, 'universe.json'), 'w', encoding='utf-8') as f:
        json.dump(universe, f, ensure_ascii=False, indent=2)

    print(f"✅ 已生成 universe.json，共 {len(stocks)} 只股票")
    print(f"   分类分布: {dict((c, len([s for s in stocks if s['category']==c])) for c in set(s['category'] for s in stocks))}")

if __name__ == '__main__':
    main()
